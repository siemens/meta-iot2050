#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2024-2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

import concurrent.futures
import io
import json
import os
import sys
import uuid

import grpc

from iot2050_eio_common import MODULE_FIRMWARE_SOCKET


DEFAULT_CONTROLLER_PATH = "/eiofs/controller"


class ModuleFirmwareUpdateError(Exception):
    """Failure while writing one of the module's firmware chips."""

    def __init__(self, chip, error, results=None):
        super().__init__(str(error))
        self.chip = chip
        self.error = error
        self.results = results or {}


def _write_firmware(path, firmware):
    with open(path, "wb") as output:
        output.write(firmware.read())


def update_module_firmware(slot, firmware_a=None, firmware_b=None,
                           controller_path=DEFAULT_CONTROLLER_PATH,
                           on_chip_start=None):
    """Write firmware for chip A, chip B, or both on a module slot.

    The operation intentionally preserves the existing CLI ordering: chip A is
    written before chip B. If chip B fails after chip A succeeds, the result
    attached to the exception records that partial completion.
    """
    if firmware_a is None and firmware_b is None:
        raise ValueError("No firmware file specified")

    slot_path = os.path.join(controller_path, f"slot{slot}")
    results = {}

    for chip, firmware, node in (
        ("A", firmware_a, "fwa"),
        ("B", firmware_b, "fwb"),
    ):
        if firmware is None:
            continue
        if on_chip_start is not None:
            on_chip_start(chip)
        try:
            _write_firmware(os.path.join(slot_path, node), firmware)
        except Exception as error:
            results[chip] = {"success": False, "error": str(error)}
            raise ModuleFirmwareUpdateError(chip, error, results) from error
        results[chip] = {"success": True}

    return results


MAX_MODULE_FIRMWARE_SIZE = 64 * 1024 * 1024


def _chip_result(result, chip):
    value = result.get(chip, {})
    return {
        "attempted": chip in result,
        "success": bool(value.get("success", False)),
        "error": str(value.get("error", "")),
    }


def _update_reply(reply_type, request, results=None, error=None):
    results = results or {}
    if error is None:
        return reply_type(
            ok=True,
            code="OK",
            message="Module firmware updated successfully",
            slot=request.slot,
            chip_a=_chip_result(results, "A"),
            chip_b=_chip_result(results, "B"),
            reboot_required=True,
        )

    return reply_type(
        ok=False,
        code="module-update-failed",
        message=str(error.error),
        slot=request.slot,
        chip_a=_chip_result(results, "A"),
        chip_b=_chip_result(results, "B"),
        partial_failure=any(
            value.get("success") for value in results.values()
        ) and bool(results),
        reboot_required=bool(results),
    )


def serve_module_firmware_grpc():
    from iot2050_module_firmware_pb2 import (
        CapabilitiesReply,
        InspectionReply,
        OperationReply,
        OperationRequest,
        SlotInspection,
        UpdateReply,
    )
    from iot2050_module_firmware_pb2_grpc import (
        ModuleFirmwareServicer,
        add_ModuleFirmwareServicer_to_server,
    )
    from iot2050_firmware_operation_store import FirmwareOperationStore

    class Service(ModuleFirmwareServicer):
        def __init__(self):
            self.operation_store = FirmwareOperationStore(
                "/var/lib/iot2050/module-firmware/operations"
            )
            self.operation_store.recover_running()
            self.operations_executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=1
            )

        def GetCapabilities(self, request, context):
            return CapabilitiesReply(
                supported=True,
                max_slots=6,
                chip_a_supported=True,
                chip_b_supported=True,
            )

        def Inspect(self, request, context):
            if request.scan:
                slots = [
                    ModuleFirmwareUpdateSlot.inspect(slot)
                    for slot in range(1, 7)
                    if os.path.isdir(
                        os.path.join(DEFAULT_CONTROLLER_PATH, f"slot{slot}")
                    )
                ]
            else:
                try:
                    ModuleFirmwareUpdateSlot.validate(request.slot)
                except ValueError as error:
                    return InspectionReply(
                        ok=False,
                        code="invalid-slot",
                        message=str(error),
                    )
                slots = [ModuleFirmwareUpdateSlot.inspect(request.slot)]
            return InspectionReply(
                ok=True,
                code="OK",
                message="OK",
                slots=[SlotInspection(**slot) for slot in slots],
            )

        @staticmethod
        def _operation_details(response):
            return {
                "slot": response.slot,
                "chips": {
                    "A": {
                        "attempted": response.chip_a.attempted,
                        "success": response.chip_a.success,
                        "error": response.chip_a.error,
                    },
                    "B": {
                        "attempted": response.chip_b.attempted,
                        "success": response.chip_b.success,
                        "error": response.chip_b.error,
                    },
                },
                "partial_failure": response.partial_failure,
                "reboot_required": response.reboot_required,
            }

        def _update(self, request, progress=None):
            if not request.firmware_a and not request.firmware_b:
                return UpdateReply(
                    ok=False,
                    code="missing-firmware",
                    message="Firmware for chip A or chip B is required",
                    slot=request.slot,
                )
            try:
                ModuleFirmwareUpdateSlot.validate(request.slot)
                slot_path = os.path.join(
                    DEFAULT_CONTROLLER_PATH, f"slot{request.slot}"
                )
                if not os.path.isdir(slot_path):
                    return UpdateReply(
                        ok=False,
                        code="slot-unavailable",
                        message="Module slot is unavailable",
                        slot=request.slot,
                    )
                if len(request.firmware_a) > MAX_MODULE_FIRMWARE_SIZE or \
                        len(request.firmware_b) > MAX_MODULE_FIRMWARE_SIZE:
                    return UpdateReply(
                        ok=False,
                        code="firmware-too-large",
                        message="Firmware file exceeds the size limit",
                        slot=request.slot,
                    )
                progress and progress("flashing-module")
                results = update_module_firmware(
                    request.slot,
                    io.BytesIO(request.firmware_a) if request.firmware_a else None,
                    io.BytesIO(request.firmware_b) if request.firmware_b else None,
                )
                return _update_reply(UpdateReply, request, results)
            except ModuleFirmwareUpdateError as error:
                return _update_reply(UpdateReply, request, error.results, error)
            except ValueError as error:
                return UpdateReply(
                    ok=False,
                    code="invalid-slot",
                    message=str(error),
                    slot=request.slot,
                )

        def Update(self, request, context):
            return self._update(request)

        def StartUpdate(self, request, context):
            if self.operation_store.has_running():
                return OperationReply(
                    ok=False,
                    code="firmware-busy",
                    message="Module firmware operation is already running",
                    state="unknown",
                )
            operation_id = str(uuid.uuid4())
            self.operation_store.create(operation_id, {
                "state": "running",
                "ok": False,
                "code": "operation-running",
                "message": "Module firmware operation is running",
                "stage": "starting",
                "details_json": "",
            })

            def progress(stage):
                try:
                    self.operation_store.update(operation_id, stage=stage)
                except (OSError, KeyError):
                    pass

            def run():
                try:
                    response = self._update(request, progress)
                    outcome = {
                        "state": "succeeded" if response.ok else "failed",
                        "ok": response.ok,
                        "code": response.code,
                        "message": response.message,
                        "stage": "completed",
                        "details_json": json.dumps(
                            self._operation_details(response),
                            separators=(",", ":"),
                        ),
                    }
                except Exception:
                    outcome = {
                        "state": "failed",
                        "ok": False,
                        "code": "module-update-failed",
                        "message": "Module firmware operation failed",
                        "details_json": "",
                    }
                self.operation_store.update(operation_id, **outcome)

            self.operations_executor.submit(run)
            return OperationReply(
                ok=True,
                code="operation-started",
                message="Module firmware operation started",
                operation_id=operation_id,
                state="running",
                stage="starting",
            )

        def GetOperation(self, request: OperationRequest, context):
            try:
                operation = self.operation_store.read(request.operation_id)
            except KeyError:
                return OperationReply(
                    ok=False,
                    code="operation-not-found",
                    message="Module firmware operation was not found",
                    state="unknown",
                )
            return OperationReply(
                ok=operation["ok"],
                code=operation["code"],
                message=operation["message"],
                details_json=operation["details_json"],
                operation_id=request.operation_id,
                state=operation["state"],
                stage=operation.get("stage", ""),
            )

    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=1),
        options=[
            ("grpc.max_receive_message_length", MAX_MODULE_FIRMWARE_SIZE * 2),
            ("grpc.max_send_message_length", 1024 * 1024),
        ],
    )
    service = Service()
    add_ModuleFirmwareServicer_to_server(service, server)
    socket_path = MODULE_FIRMWARE_SOCKET.removeprefix("/run/iot2050/")
    os.makedirs("/run/iot2050", mode=0o755, exist_ok=True)
    try:
        os.unlink(MODULE_FIRMWARE_SOCKET)
    except FileNotFoundError:
        pass
    if server.add_insecure_port(f"unix://{MODULE_FIRMWARE_SOCKET}") == 0:
        raise RuntimeError(f"Cannot bind {socket_path}")
    server.start()
    os.chmod(MODULE_FIRMWARE_SOCKET, 0o600)
    try:
        server.wait_for_termination()
    finally:
        service.operations_executor.shutdown(wait=False, cancel_futures=True)
        server.stop(grace=0)
        try:
            os.unlink(MODULE_FIRMWARE_SOCKET)
        except FileNotFoundError:
            pass


class ModuleFirmwareUpdateSlot:
    @staticmethod
    def validate(slot):
        if slot < 1 or slot > 6:
            raise ValueError("Module slot must be between 1 and 6")

    @staticmethod
    def inspect(slot):
        ModuleFirmwareUpdateSlot.validate(slot)
        slot_path = os.path.join(DEFAULT_CONTROLLER_PATH, f"slot{slot}")
        return {
            "slot": slot,
            "available": os.path.isdir(slot_path),
            "chip_a_node": os.path.exists(os.path.join(slot_path, "fwa")),
            "chip_b_node": os.path.exists(os.path.join(slot_path, "fwb")),
        }

def main(args):
    if args and args[0] == "--grpc-server":
        serve_module_firmware_grpc()
        return 0

    print("This module is a gRPC service. Use the Module Firmware gRPC "
          "service to update module firmware.", file=sys.stderr)
    return 2

if __name__ == '__main__':
    CODE = main(sys.argv[1:])
    sys.exit(CODE)

