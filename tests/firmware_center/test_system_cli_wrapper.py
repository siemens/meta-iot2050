# SPDX-License-Identifier: MIT

import runpy
import sys
import types

import pytest

from conftest import SYSTEM_FWU_CLI


def test_wrapper_passes_full_argv_to_core_main(monkeypatch):
    received = []
    core = types.ModuleType("iot2050_firmware_update")

    def fake_main(argv):
        received.append(argv)
        return 7

    core.main = fake_main
    monkeypatch.setitem(sys.modules, "iot2050_firmware_update", core)
    monkeypatch.setattr(sys, "argv", ["iot2050-firmware-update", "firmware.tar.xz"])

    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(SYSTEM_FWU_CLI), run_name="__main__")

    assert error.value.code == 7
    assert received == [["iot2050-firmware-update", "firmware.tar.xz"]]