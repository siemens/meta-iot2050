# Copyright (c) Siemens AG, 2024-2026
#
# SPDX-License-Identifier: MIT

"""Reusable core for updating IOT2050 module chip firmware."""

import os


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
