# SPDX-License-Identifier: MIT

import builtins
import io
import os
import sys
import types

import pytest

from conftest import REPO_ROOT, load_source


SM_PROVIDERS = REPO_ROOT / "meta-sm/recipes-app/iot2050-firmware-provider-sm/files/iot2050_firmware_provider_sm.py"
MANAGER_CORE = REPO_ROOT / "meta-example/recipes-app/iot2050-firmware-manager/files/iot2050_firmware_manager.py"


@pytest.fixture
def sm_providers(monkeypatch):
    manager_core = load_source("iot2050_firmware_manager", MANAGER_CORE)
    monkeypatch.setitem(sys.modules, "iot2050_firmware_manager", manager_core)
    return load_source("sm_firmware_providers_under_test", SM_PROVIDERS)


def test_non_sm_board_never_exposes_sm_providers(sm_providers, monkeypatch):
    monkeypatch.setattr(sm_providers.os.path, "exists", lambda path: True)

    def fake_open(path, mode="r", *args, **kwargs):
        if path == "/sys/firmware/devicetree/base/compatible":
            from io import BytesIO
            return BytesIO(b"siemens,iot2050-advanced-pg2\0")
        return builtins.open(path, mode, *args, **kwargs)

    monkeypatch.setattr(sm_providers, "open", fake_open, raising=False)

    assert sm_providers.EIOControllerProvider().available()[0] is False
    assert sm_providers.ModuleFirmwareProvider().available()[0] is False


def test_module_provider_requires_eiofs_on_sm_board(sm_providers, monkeypatch):
    def fake_open(path, mode="r", *args, **kwargs):
        if path == "/sys/firmware/devicetree/base/compatible":
            from io import BytesIO
            return BytesIO(b"siemens,iot2050-advanced-sm\0")
        return builtins.open(path, mode, *args, **kwargs)

    monkeypatch.setattr(sm_providers, "open", fake_open, raising=False)
    monkeypatch.setattr(
        sm_providers.os.path, "exists",
        lambda path: path == sm_providers.SM_MARKER,
    )
    monkeypatch.setattr(sm_providers.os.path, "isdir", lambda path: False)

    available, reason = sm_providers.ModuleFirmwareProvider().available()
    assert available is False
    assert "filesystem" in reason


def test_module_capabilities_describe_chip_a_and_b(sm_providers):
    capability = sm_providers.ModuleFirmwareProvider().capabilities()
    assert capability["provider"] == "module"
    assert capability["chips"] == ["A", "B"]
    assert capability["requires_signature"] is False


def test_module_update_consumes_staging_tokens_and_returns_chip_results(
    sm_providers, monkeypatch
):
    core = types.ModuleType("iot2050_module_firmware_update")
    captured = {}

    class ModuleFirmwareUpdateError(Exception):
        pass

    def update(slot, firmware_a, firmware_b, on_chip_start):
        captured["slot"] = slot
        captured["a"] = firmware_a.read()
        captured["b"] = firmware_b.read()
        on_chip_start("A")
        on_chip_start("B")
        return {"A": {"success": True}, "B": {"success": True}}

    core.ModuleFirmwareUpdateError = ModuleFirmwareUpdateError
    core.update_module_firmware = update
    monkeypatch.setitem(sys.modules, "iot2050_module_firmware_update", core)
    monkeypatch.setattr(sm_providers.os.path, "isdir", lambda path: True)

    # The provider expects a pathlib-like object from staging.
    class StagedPath:
        def __init__(self, token):
            self.token = token

        def open(self, mode):
            return io.BytesIO(self.token.encode())

    class PathStaging:
        def resolve(self, token):
            return StagedPath(token), {
                "token": token, "sha256": f"hash-{token}", "size": 1,
            }

    phases = []
    result = sm_providers.ModuleFirmwareProvider().start(
        {"slot": 3, "firmware_a": "token-a", "firmware_b": "token-b"},
        phases.append,
        PathStaging(),
    )

    assert captured == {"slot": 3, "a": b"token-a", "b": b"token-b"}
    assert phases == ["flashing-chip-a", "flashing-chip-b"]
    assert result["chips"]["A"]["success"] is True
    assert result["reboot_required"] is True


def test_module_provider_rejects_out_of_range_slot(sm_providers):
    with pytest.raises(sm_providers.ManagerError) as error:
        sm_providers.ModuleFirmwareProvider().inspect({"slot": 7})
    assert error.value.code == "invalid-slot"