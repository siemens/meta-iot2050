# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""SM-only firmware providers for the common IOT2050 firmware manager."""

import os
import sys

from iot2050_firmware_manager import ManagerError


SM_COMPATIBLE = "siemens,iot2050-advanced-sm"
SM_MARKER = "/run/iot2050/sm-board"
EIO_LIBRARY = "/usr/lib/iot2050/eio"


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
        raise ManagerError(
            "invalid-slot", "A numeric module slot is required") from error
    if slot < 1 or slot > 6:
        raise ManagerError("invalid-slot", "Module slot must be between 1 and 6")
    return slot


class EIOControllerProvider:
    name = "controller"

    def available(self):
        if not _is_sm_board():
            return False, "not an SM variant"
        if EIO_LIBRARY not in sys.path:
            sys.path.insert(0, EIO_LIBRARY)
        try:
            from iot2050_eio_fwu import FirmwareUpdateChecker
            inspection = FirmwareUpdateChecker(strict=False).inspect()
        except Exception:
            return False, "EIO firmware service is unavailable"
        if inspection["status"] == "unavailable":
            return False, inspection["message"]
        return True, None

    def capabilities(self):
        return {
            "provider": self.name,
            "label": "EIO Controller Firmware",
            "operations": ["inspect", "update"],
            "source": "image-default",
            "requires_signature": False,
        }

    def inspect(self, request):
        if EIO_LIBRARY not in sys.path:
            sys.path.insert(0, EIO_LIBRARY)
        from iot2050_eio_fwu import FirmwareUpdateChecker
        return FirmwareUpdateChecker(strict=False).inspect()

    def start(self, request, progress, staging_store):
        if request.get("source") != "image-default":
            raise ManagerError(
                "invalid-source", "Controller update only accepts image-default")
        if EIO_LIBRARY not in sys.path:
            sys.path.insert(0, EIO_LIBRARY)
        from iot2050_eio_fwu import (
            EIO_FWU_MAP3_FW_BIN,
            FirmwareUpdateChecker,
            update_firmware,
        )
        inspection = FirmwareUpdateChecker(strict=False).inspect()
        if inspection["integrity"] is not True:
            raise ManagerError(
                "firmware-corrupt", "Bundled controller firmware failed integrity check")
        progress("flashing-controller")
        with open(EIO_FWU_MAP3_FW_BIN, "rb") as firmware:
            status, message = update_firmware(firmware.read(), 0)
        if status != 0:
            raise ManagerError("controller-update-failed", str(message))
        progress("pending-reboot")
        return {
            "current_version_before": inspection["current_version"],
            "bundled_version": inspection["bundled_version"],
            "bundled_sha256": inspection["actual_sha256"],
            "readback_verified": True,
            "reboot_required": True,
            "activation_state": "pending-reboot",
        }


class ModuleFirmwareProvider:
    name = "module"

    def available(self):
        if not _is_sm_board():
            return False, "not an SM variant"
        if not os.path.isdir("/eiofs/controller"):
            return False, "EIO controller filesystem is unavailable"
        return True, None

    def capabilities(self):
        return {
            "provider": self.name,
            "label": "Module Firmware",
            "operations": ["inspect", "update"],
            "source": "upload",
            "chips": ["A", "B"],
            "requires_signature": False,
        }

    def inspect(self, request):
        slot = _parse_slot(request)
        slot_path = f"/eiofs/controller/slot{slot}"
        return {
            "slot": slot,
            "available": os.path.isdir(slot_path),
            "chip_a_node": os.path.exists(os.path.join(slot_path, "fwa")),
            "chip_b_node": os.path.exists(os.path.join(slot_path, "fwb")),
        }

    def start(self, request, progress, staging_store):
        slot = _parse_slot(request)
        slot_path = f"/eiofs/controller/slot{slot}"
        if not os.path.isdir(slot_path):
            raise ManagerError("slot-unavailable", "Module slot is unavailable")
        tokens = {
            "A": request.get("firmware_a"),
            "B": request.get("firmware_b"),
        }
        if not any(tokens.values()):
            raise ManagerError(
                "missing-firmware", "Firmware for chip A or chip B is required")

        staged = {}
        handles = {}
        try:
            for chip, token in tokens.items():
                if token:
                    path, metadata = staging_store.resolve(token)
                    staged[chip] = metadata
                    handles[chip] = path.open("rb")

            from iot2050_module_firmware_update import (
                ModuleFirmwareUpdateError,
                update_module_firmware,
            )
            try:
                results = update_module_firmware(
                    slot,
                    handles.get("A"),
                    handles.get("B"),
                    on_chip_start=lambda chip: progress(
                        f"flashing-chip-{chip.lower()}"),
                )
            except ModuleFirmwareUpdateError as error:
                raise ManagerError(
                    "module-update-failed",
                    f"Failed to write firmware for chip {error.chip}",
                    {"chips": error.results, "staged": staged},
                ) from error
        finally:
            for handle in handles.values():
                handle.close()

        return {
            "slot": slot,
            "chips": results,
            "staged": staged,
            "reboot_required": True,
        }
