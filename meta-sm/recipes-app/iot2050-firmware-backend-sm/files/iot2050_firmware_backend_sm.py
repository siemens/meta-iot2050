# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""SM-only firmware backends for the common IOT2050 firmware task core."""

import os
import sys
import json
import time

import grpc

from iot2050_fwmgr import FirmwareError
from iot2050_eio_common import iot2050_module_firmware_api_server


SM_COMPATIBLE = "siemens,iot2050-advanced-sm"
SM_MARKER = "/run/iot2050/sm-board"
EIO_LIBRARY = "/usr/lib/iot2050/eio"


def _eio_grpc_client():
    if EIO_LIBRARY not in sys.path:
        sys.path.insert(0, EIO_LIBRARY)
    from gRPC.EIOManager.iot2050_eio_pb2 import (
        CheckFWURequest,
        UpdateFirmwareRequest,
    )
    from gRPC.EIOManager.iot2050_eio_pb2_grpc import EIOManagerStub
    from iot2050_eio_global import iot2050_eio_api_server

    channel = grpc.insecure_channel(iot2050_eio_api_server)
    return channel, EIOManagerStub(channel), CheckFWURequest, UpdateFirmwareRequest


def _inspect_controller_grpc():
    channel, stub, check_request, _ = _eio_grpc_client()
    try:
        response = stub.CheckFWU(check_request(entity=0), timeout=10)
    except grpc.RpcError as error:
        raise FirmwareError(
            "controller-service-unavailable",
            "EIO controller firmware service is unavailable",
        ) from error
    finally:
        channel.close()

    if response.HasField("inspection"):
        inspection_message = response.inspection
        inspection = {
            "supported": inspection_message.supported,
            "current_version": inspection_message.current_version or None,
            "bundled_version": inspection_message.bundled_version or None,
            "metadata_sha1": inspection_message.metadata_sha1 or None,
            "actual_sha256": inspection_message.actual_sha256 or None,
            "integrity": inspection_message.integrity,
            "update_needed": inspection_message.update_needed,
            "status": inspection_message.status,
            "status_code": inspection_message.status_code,
            "message": inspection_message.detail_message,
        }
    else:
        try:
            inspection = json.loads(response.message)
        except (TypeError, ValueError) as error:
            raise FirmwareError(
                "controller-invalid-response",
                "EIO controller firmware service returned invalid inspection data",
            ) from error
    if not isinstance(inspection, dict):
        raise FirmwareError(
            "controller-invalid-response",
            "EIO controller firmware service returned invalid inspection data",
        )
    return inspection


def _is_sm_board():
    try:
        with open("/sys/firmware/devicetree/base/compatible", "rb") as compatible:
            compatibles = compatible.read().split(b"\0")
    except OSError:
        return False
    return SM_COMPATIBLE.encode("ascii") in compatibles


def _parse_slot(request):
    try:
        slot = int(request["slot"])
    except (KeyError, TypeError, ValueError) as error:
        raise FirmwareError(
            "invalid-slot", "A numeric module slot is required") from error
    if slot < 1 or slot > 6:
        raise FirmwareError("invalid-slot", "Module slot must be between 1 and 6")
    return slot


def _module_grpc_client():
    from iot2050_module_firmware_pb2 import (
        InspectRequest,
        OperationRequest,
        UpdateRequest,
    )
    from iot2050_module_firmware_pb2_grpc import ModuleFirmwareStub

    channel = grpc.insecure_channel(
        iot2050_module_firmware_api_server,
        options=[
            ("grpc.max_send_message_length", 128 * 1024 * 1024),
            ("grpc.max_receive_message_length", 1024 * 1024),
        ],
    )
    return (
        channel,
        ModuleFirmwareStub(channel),
        InspectRequest,
        UpdateRequest,
        OperationRequest,
    )


def _wait_module_operation(stub, operation_id, operation_request,
                           progress=None, timeout=3600):
    deadline = time.monotonic() + timeout
    while True:
        response = stub.GetOperation(
            operation_request(operation_id=operation_id),
            timeout=min(10, max(1, deadline - time.monotonic())),
        )
        if response.state == "running":
            if time.monotonic() >= deadline:
                raise FirmwareError(
                    "module-update-timeout",
                    "Module firmware update timed out",
                )
            if progress and response.stage:
                progress(response.stage)
            time.sleep(1)
            continue
        if not response.ok:
            details = {}
            try:
                details = json.loads(response.details_json)
            except (TypeError, ValueError):
                pass
            raise FirmwareError(response.code, response.message, details)
        try:
            return json.loads(response.details_json) if response.details_json else {}
        except (TypeError, ValueError) as error:
            raise FirmwareError(
                "module-invalid-response",
                "Module firmware service returned invalid operation data",
            ) from error


def _module_inspection_response(response, scan=False):
    if not response.ok:
        raise FirmwareError(response.code, response.message)
    if scan or len(response.slots) != 1:
        return {
            "eiofs_available": os.path.isdir("/eiofs/controller"),
            "slots": [
                {
                    "slot": slot.slot,
                    "available": slot.available,
                    "chip_a_node": slot.chip_a_node,
                    "chip_b_node": slot.chip_b_node,
                }
                for slot in response.slots
            ],
        }
    slot = response.slots[0]
    return {
        "slot": slot.slot,
        "available": slot.available,
        "chip_a_node": slot.chip_a_node,
        "chip_b_node": slot.chip_b_node,
    }


class EIOControllerBackend:
    name = "controller"

    def is_visible(self):
        return _is_sm_board()

    def available(self):
        if not _is_sm_board():
            return False, "not an SM variant"
        try:
            inspection = _inspect_controller_grpc()
        except FirmwareError as error:
            return False, error.message
        except Exception:
            return False, "EIO firmware service is unavailable"
        if inspection["status"] in ("unavailable", "runtime-unavailable"):
            return False, inspection["message"]
        return True, None

    def capabilities(self):
        return {
            "backend": self.name,
            "label": "EIO Controller Firmware",
            "operations": ["inspect", "update"],
            "source": "image-default",
            "requires_signature": False,
        }

    def inspect(self, request):
        return _inspect_controller_grpc()

    def start(self, request, progress, staging_store):
        if request.get("source") != "image-default":
            raise FirmwareError(
                "invalid-source", "Controller update only accepts image-default")
        from iot2050_eio_global import EIO_FWU_MAP3_FW_BIN

        inspection = _inspect_controller_grpc()
        if inspection["integrity"] is not True:
            raise FirmwareError(
                "firmware-corrupt", "Bundled controller firmware failed integrity check")
        progress("flashing-controller")
        with open(EIO_FWU_MAP3_FW_BIN, "rb") as firmware:
            firmware_data = firmware.read()
        channel, stub, _, update_request = _eio_grpc_client()
        try:
            response = stub.UpdateFirmware(
                update_request(entity=0, firmware=firmware_data),
                timeout=300,
            )
        except grpc.RpcError as error:
            raise FirmwareError(
                "controller-service-unavailable",
                "EIO controller firmware service is unavailable",
            ) from error
        finally:
            channel.close()
        if response.status != 0:
            raise FirmwareError("controller-update-failed", response.message)
        progress("pending-reboot")
        return {
            "current_version_before": inspection["current_version"],
            "bundled_version": inspection["bundled_version"],
            "bundled_sha256": inspection["actual_sha256"],
            "readback_verified": True,
            "reboot_required": True,
            "activation_state": "pending-reboot",
        }


class ModuleFirmwareBackend:
    name = "module"
    MAX_SLOTS = 6

    def is_visible(self):
        return _is_sm_board()

    def available(self):
        if not _is_sm_board():
            return False, "not an SM variant"
        if not os.path.isdir("/eiofs/controller"):
            return False, "EIO controller filesystem is unavailable"
        if not any(
            slot["chip_a_node"] or slot["chip_b_node"]
            for slot in self.scan_slots()
        ):
            return False, "No module firmware nodes (fwa/fwb) detected"
        return True, None

    def capabilities(self):
        return {
            "backend": self.name,
            "label": "Module Firmware",
            "operations": ["inspect", "update"],
            "source": "upload",
            "chips": ["A", "B"],
            "transport": "module-firmware gRPC",
            "requires_signature": False,
        }

    def inspect(self, request):
        scan = bool(request.get("scan"))
        channel, stub, inspect_request, _, _ = _module_grpc_client()
        try:
            response = stub.Inspect(
                inspect_request(
                    slot=int(request.get("slot", 0) or 0),
                    scan=scan,
                ),
                timeout=10,
            )
        except grpc.RpcError as error:
            raise FirmwareError(
                "module-service-unavailable",
                "Module firmware service is unavailable",
            ) from error
        finally:
            channel.close()
        return _module_inspection_response(response, scan=scan)

    @classmethod
    def inspect_slot(cls, slot):
        slot_path = f"/eiofs/controller/slot{slot}"
        return {
            "slot": slot,
            "available": os.path.isdir(slot_path),
            "chip_a_node": os.path.exists(os.path.join(slot_path, "fwa")),
            "chip_b_node": os.path.exists(os.path.join(slot_path, "fwb")),
        }

    @classmethod
    def scan_slots(cls):
        return [
            cls.inspect_slot(slot)
            for slot in range(1, cls.MAX_SLOTS + 1)
            if os.path.isdir(f"/eiofs/controller/slot{slot}")
        ]

    def start(self, request, progress, staging_store):
        slot = _parse_slot(request)
        slot_path = f"/eiofs/controller/slot{slot}"
        if not os.path.isdir(slot_path):
            raise FirmwareError("slot-unavailable", "Module slot is unavailable")
        tokens = {
            "A": request.get("firmware_a"),
            "B": request.get("firmware_b"),
        }
        if not any(tokens.values()):
            raise FirmwareError(
                "missing-firmware", "Firmware for chip A or chip B is required")

        staged = {}
        firmware = {}
        for chip, token in tokens.items():
            if not token:
                continue
            path, metadata = staging_store.resolve(token)
            staged[chip] = metadata
            try:
                firmware[chip] = path.read_bytes()
            except OSError as error:
                raise FirmwareError(
                    "staging-unavailable",
                    "Staged firmware is unavailable",
                ) from error

        progress("flashing-module")
        channel, stub, _, update_request, operation_request = _module_grpc_client()
        try:
            response = stub.StartUpdate(
                update_request(
                    slot=slot,
                    firmware_a=firmware.get("A", b""),
                    firmware_b=firmware.get("B", b""),
                ),
                timeout=10,
            )
            if not response.ok:
                raise FirmwareError(response.code, response.message)
            result = _wait_module_operation(
                stub, response.operation_id, operation_request, progress)
        except grpc.RpcError as error:
            raise FirmwareError(
                "module-service-unavailable",
                "Module firmware service is unavailable",
            ) from error
        finally:
            channel.close()

        return {
            **result,
            "slot": result.get("slot", slot),
            "staged": staged,
            "reboot_required": result.get("reboot_required", True),
        }
