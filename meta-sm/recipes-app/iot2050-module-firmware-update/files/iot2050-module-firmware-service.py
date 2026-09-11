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
import queue
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


def serve():
    from gRPC.iot2050_module_firmware_pb2 import (
        CapabilitiesReply,
        InspectionReply,
        OperationLog,
        OperationReply,
        OperationRequest,
        OPERATION_FAILED,
        OPERATION_INTERRUPTED,
        OPERATION_RUNNING,
        OPERATION_SUCCEEDED,
        ModuleUpdateResult,
        OperationError,
        SlotInspection,
        UpdateReply,
    )
    from gRPC.iot2050_module_firmware_pb2_grpc import (
        ModuleFirmwareServicer,
        add_ModuleFirmwareServicer_to_server,
    )
    from iot2050_firmware_operation_store import (
        FirmwareOperationLogHub,
        FirmwareOperationStore,
    )

    class Service(ModuleFirmwareServicer):
        def __init__(self):
            self.operation_store = FirmwareOperationStore(
                "/var/lib/iot2050/module-firmware/operations"
            )
            self.log_hub = FirmwareOperationLogHub()
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
            operation_id = str(uuid.uuid4())
            operation = {
                "operation_id": operation_id,
                "operation": "update",
                "state": "running",
                "ok": False,
                "code": "operation-running",
                "message": "Module firmware operation is running",
                "last_message": "Module firmware operation started",
            }
            if not self.operation_store.admit(operation_id, operation):
                return OperationReply(
                    status=OPERATION_FAILED,
                    code="firmware-busy",
                    message="Module firmware operation is already running",
                    operation_error=OperationError(
                        code="firmware-busy",
                        message="Module firmware operation is already running",
                    ),
                )
            self.log_hub.publish(
                operation_id, "Module firmware operation started"
            )
            if request.firmware_a:
                self.log_hub.publish(operation_id, "Updating firmware A ...")
            if request.firmware_b:
                self.log_hub.publish(operation_id, "Updating firmware B ...")

            def progress(stage):
                try:
                    message = stage.replace("-", " ").capitalize()
                    self.operation_store.update(
                        operation_id, last_message=message
                    )
                    self.log_hub.publish(
                        operation_id, message
                    )
                except (OSError, KeyError):
                    pass

            def run():
                try:
                    response = self._update(request, progress)
                    outcome = {
                        "state": "succeeded" if response.ok else "failed",
                        "code": response.code,
                        "message": response.message,
                        "last_message": response.message,
                        "result": self._operation_details(response),
                        "error": None if response.ok else {
                            "code": response.code,
                            "message": response.message,
                        },
                    }
                except Exception:
                    outcome = {
                        "state": "failed",
                        "code": "module-update-failed",
                        "message": "Module firmware operation failed",
                        "last_message": "Module firmware operation failed",
                        "error": {
                            "code": "module-update-failed",
                            "message": "Module firmware operation failed",
                        },
                    }
                try:
                    self.operation_store.update(operation_id, **outcome)
                    self.log_hub.publish(operation_id, outcome["message"])
                finally:
                    self.log_hub.close(operation_id)

            self.operations_executor.submit(run)
            return OperationReply(
                operation_id=operation_id,
                status=OPERATION_RUNNING,
                code="operation-started",
                message="Module firmware operation started",
            )

        def GetOperation(self, request: OperationRequest, context):
            try:
                operation = self.operation_store.read(request.operation_id)
            except KeyError:
                return OperationReply(
                    operation_id=request.operation_id,
                    status=OPERATION_FAILED,
                    code="operation-not-found",
                    message="Module firmware operation was not found",
                    operation_error=OperationError(
                        code="operation-not-found",
                        message="Module firmware operation was not found",
                    ),
                )
            return OperationReply(
                operation_id=request.operation_id,
                status={
                    "running": OPERATION_RUNNING,
                    "succeeded": OPERATION_SUCCEEDED,
                    "failed": OPERATION_FAILED,
                    "interrupted": OPERATION_INTERRUPTED,
                }.get(operation["state"], 0),
                code=operation["code"],
                message=operation["message"],
                created_at=operation.get("created_at", ""),
                updated_at=operation.get("updated_at", ""),
                finished_at=operation.get("finished_at", ""),
                last_message=operation.get("last_message", ""),
                update_result=(
                    ModuleUpdateResult(**operation["result"])
                    if operation.get("result") else None
                ),
                operation_error=(
                    OperationError(**operation["error"])
                    if operation.get("error") else None
                ),
            )

        def StreamOperationLogs(self, request, context):
            try:
                operation = self.operation_store.read(request.operation_id)
            except KeyError:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Module firmware operation was not found",
                )
            if operation.get("state") != "running":
                return
            subscriber, entries = self.log_hub.subscribe(
                request.operation_id, request.after_sequence
            )
            try:
                for entry in entries:
                    yield OperationLog(
                        sequence=entry["sequence"],
                        timestamp=entry["timestamp"],
                        message=entry["message"],
                    )
                while context.is_active():
                    try:
                        entry = subscriber.get(timeout=1)
                    except queue.Empty:
                        continue
                    if entry is self.log_hub._CLOSED:
                        return
                    yield OperationLog(
                        sequence=entry["sequence"],
                        timestamp=entry["timestamp"],
                        message=entry["message"],
                    )
            finally:
                self.log_hub.unsubscribe(request.operation_id, subscriber)

    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=4),
        options=[
            ("grpc.max_receive_message_length", MAX_MODULE_FIRMWARE_SIZE * 2),
            ("grpc.max_send_message_length", 1024 * 1024),
        ],
    )
    service = Service()
    add_ModuleFirmwareServicer_to_server(service, server)
    socket_path = MODULE_FIRMWARE_SOCKET
    os.makedirs(os.path.dirname(MODULE_FIRMWARE_SOCKET), mode=0o755, exist_ok=True)
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

if __name__ == '__main__':
    serve()

