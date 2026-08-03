# SPDX-License-Identifier: MIT

import json
import hashlib
import stat
import threading
import time

import pytest

from conftest import REPO_ROOT, load_source


MANAGER_CORE = REPO_ROOT / "meta-example/recipes-app/iot2050-firmware-manager/files/iot2050_firmware_manager.py"


@pytest.fixture
def manager_core():
    return load_source("firmware_manager_under_test", MANAGER_CORE)


class FakeProvider:
    def __init__(self, name="fake", available=True):
        self.name = name
        self.is_available = available

    def available(self):
        return self.is_available, None if self.is_available else "not present"

    def capabilities(self):
        return {"provider": self.name, "operations": ["inspect"]}

    def inspect(self, request):
        return {"provider": self.name, "request": request}


class UpdatingProvider(FakeProvider):
    def start(self, request, progress, staging_store):
        progress("verifying")
        return {"updated": request["value"]}


def test_capabilities_only_lists_available_providers(manager_core):
    registry = manager_core.ProviderRegistry(
        provider_dir="/nonexistent",
        builtins=[FakeProvider("system"), FakeProvider("sm", available=False)],
    )
    manager = manager_core.FirmwareManager(registry)

    response = manager.handle({
        "v": 1,
        "id": "request-1",
        "op": "capabilities.list",
        "payload": {},
    })

    assert response == {
        "v": 1,
        "id": "request-1",
        "ok": True,
        "data": [{"provider": "system", "operations": ["inspect"]}],
    }


def test_inspect_routes_provider_specific_payload(manager_core):
    registry = manager_core.ProviderRegistry(
        provider_dir="/nonexistent", builtins=[FakeProvider("controller")]
    )
    manager = manager_core.FirmwareManager(registry)

    response = manager.handle({
        "v": 1,
        "id": "request-2",
        "op": "inspect.get",
        "provider": "controller",
        "payload": {"strict": False},
    })

    assert response["ok"] is True
    assert response["data"] == {
        "provider": "controller",
        "request": {"strict": False},
    }


def test_system_provider_requires_staged_package(manager_core, tmp_path):
    provider = manager_core.SystemFirmwareProvider(tmp_path / "backup")

    with pytest.raises(manager_core.ManagerError) as error:
        provider.inspect({})

    assert error.value.code == "staging-required"


def test_system_provider_inspects_and_updates_staged_package(
    manager_core, monkeypatch, tmp_path
):
    updater = type(__import__("sys"))("iot2050_firmware_update")
    calls = []
    updater.inspect_system_firmware = lambda path: {
        "firmware_name": "system.bin",
        "signature_verified": True,
    }

    def update(path, backup_dir, **kwargs):
        calls.append((path, backup_dir, kwargs))
        return {"firmware_name": "system.bin", "reboot_required": True}

    updater.update_system_firmware = update
    monkeypatch.setitem(__import__("sys").modules, "iot2050_firmware_update", updater)
    staging = manager_core.StagingStore(tmp_path / "staging")
    source = tmp_path / "system.tar.xz"
    source.write_bytes(b"signed-package")
    staged = staging.import_file(source)
    provider = manager_core.SystemFirmwareProvider(tmp_path / "backup")
    provider.bind_staging_store(staging)

    inspected = provider.inspect({"token": staged["token"]})
    result = provider.start(
        {"token": staged["token"]}, lambda phase: None, staging)

    assert inspected["signature_verified"] is True
    assert result["reboot_required"] is True
    assert calls[0][1] == str(tmp_path / "backup")


def test_protocol_errors_are_stable_and_do_not_raise(manager_core):
    manager = manager_core.FirmwareManager(
        manager_core.ProviderRegistry(
            provider_dir="/nonexistent", builtins=[FakeProvider()]
        )
    )

    response = manager.handle({"v": 2, "id": "bad", "op": "capabilities.list"})
    assert response["ok"] is False
    assert response["error"]["code"] == "unsupported-version"

    response = manager.handle({"v": 1, "id": "bad", "op": "missing"})
    assert response["ok"] is False
    assert response["error"]["code"] == "unknown-operation"


def test_json_lines_codec(manager_core):
    request = manager_core.decode_request(
        '{"v":1,"id":"codec","op":"capabilities.list","payload":{}}'
    )
    assert request["id"] == "codec"

    encoded = manager_core.encode_response({
        "v": 1, "id": "codec", "ok": True, "data": []
    })
    assert encoded.endswith("\n")
    assert json.loads(encoded)["ok"] is True

    with pytest.raises(manager_core.ManagerError) as error:
        manager_core.decode_request("not-json")
    assert error.value.code == "invalid-json"


def test_descriptor_discovery_loads_provider(manager_core, tmp_path):
    provider = tmp_path / "provider.py"
    provider.write_text(
        "class Provider:\n"
        "    name = 'module'\n"
        "    def available(self): return True, None\n"
        "    def capabilities(self): return {'provider': self.name}\n"
        "    def inspect(self, request): return {'slot': request['slot']}\n",
        encoding="utf-8",
    )
    (tmp_path / "20-module.json").write_text(json.dumps({
        "module": "provider.py",
        "class": "Provider",
    }), encoding="utf-8")

    registry = manager_core.ProviderRegistry(provider_dir=tmp_path, builtins=[])
    registry.discover()

    assert registry.get("module").inspect({"slot": 2}) == {"slot": 2}


def test_bad_provider_descriptor_does_not_hide_builtin_provider(
    manager_core, tmp_path
):
    (tmp_path / "broken.json").write_text(
        '{"module":"missing.py","class":"Provider"}', encoding="utf-8")
    registry = manager_core.ProviderRegistry(
        provider_dir=tmp_path, builtins=[FakeProvider("system")])

    registry.discover()

    assert registry.get("system").name == "system"
    assert registry.discovery_errors[0]["descriptor"] == "broken.json"


def test_background_task_persists_success_and_survives_manager_instance(
    manager_core, tmp_path
):
    registry = manager_core.ProviderRegistry(
        provider_dir="/nonexistent", builtins=[UpdatingProvider("module")]
    )
    store = manager_core.TaskStore(tmp_path / "tasks")
    manager = manager_core.FirmwareManager(registry, task_store=store)

    response = manager.handle({
        "v": 1,
        "id": "start",
        "op": "action.start",
        "provider": "module",
        "payload": {"value": 42},
    })
    assert response["ok"] is True
    task_id = response["data"]["id"]

    for _ in range(100):
        task = store.read(task_id)
        if task["state"] in ("succeeded", "failed"):
            break
        time.sleep(0.001)

    assert task["state"] == "succeeded"
    assert task["result"] == {"updated": 42}

    reloaded_manager = manager_core.FirmwareManager(
        registry,
        task_store=manager_core.TaskStore(tmp_path / "tasks"),
    )
    response = reloaded_manager.handle({
        "v": 1,
        "id": "get",
        "op": "task.get",
        "payload": {"task_id": task_id},
    })
    assert response["data"]["state"] == "succeeded"


def test_provider_failure_is_sanitized_in_persistent_task(manager_core, tmp_path):
    class FailingProvider(FakeProvider):
        def start(self, request, progress, staging_store):
            raise RuntimeError("secret traceback details")

    registry = manager_core.ProviderRegistry(
        provider_dir="/nonexistent", builtins=[FailingProvider("system")]
    )
    store = manager_core.TaskStore(tmp_path / "tasks")
    manager = manager_core.FirmwareManager(registry, task_store=store)
    response = manager.handle({
        "v": 1,
        "id": "start",
        "op": "action.start",
        "provider": "system",
        "payload": {},
    })
    task_id = response["data"]["id"]

    for _ in range(100):
        task = store.read(task_id)
        if task["state"] == "failed":
            break
        time.sleep(0.001)

    assert task["error"] == {
        "code": "provider-failed",
        "message": "Firmware operation failed",
    }


def test_staging_import_records_hash_size_and_private_permissions(
    manager_core, tmp_path
):
    source = tmp_path / "firmware.bin"
    source.write_bytes(b"firmware-content")
    store = manager_core.StagingStore(tmp_path / "staging", max_size=1024)

    metadata = store.import_file(source, "../unsafe-name.bin")
    path, resolved = store.resolve(metadata["token"])

    assert resolved == metadata
    assert metadata["name"] == "unsafe-name.bin"
    assert metadata["size"] == len(b"firmware-content")
    assert metadata["sha256"] == hashlib.sha256(b"firmware-content").hexdigest()
    assert path.read_bytes() == b"firmware-content"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_staging_rejects_oversized_file_and_invalid_token(manager_core, tmp_path):
    source = tmp_path / "large.bin"
    source.write_bytes(b"12345")
    store = manager_core.StagingStore(tmp_path / "staging", max_size=4)

    with pytest.raises(manager_core.ManagerError) as error:
        store.import_file(source)
    assert error.value.code == "firmware-too-large"

    with pytest.raises(manager_core.ManagerError) as error:
        store.resolve("../../etc/passwd")
    assert error.value.code == "invalid-staging-token"


def test_second_hardware_task_is_rejected_immediately(manager_core, tmp_path):
    entered = threading.Event()
    release = threading.Event()

    class BlockingProvider(FakeProvider):
        def start(self, request, progress, staging_store):
            entered.set()
            release.wait(timeout=2)
            return {}

    registry = manager_core.ProviderRegistry(
        provider_dir="/nonexistent", builtins=[BlockingProvider("module")]
    )
    store = manager_core.TaskStore(tmp_path / "tasks")
    manager = manager_core.FirmwareManager(registry, task_store=store)
    first = manager.handle({
        "v": 1, "id": "first", "op": "action.start",
        "provider": "module", "payload": {},
    })
    assert first["ok"] is True
    assert entered.wait(timeout=1)

    second = manager.handle({
        "v": 1, "id": "second", "op": "action.start",
        "provider": "module", "payload": {},
    })
    release.set()

    assert second["ok"] is False
    assert second["error"]["code"] == "firmware-busy"


def test_running_task_is_marked_interrupted_after_manager_restart(
    manager_core, tmp_path
):
    store = manager_core.TaskStore(tmp_path / "tasks")
    task_id = "2b50e8f5-2d7e-44af-bfcb-3e01bb62f799"
    store.write({
        "id": task_id,
        "provider": "module",
        "state": "running",
        "phase": "flashing-chip-a",
        "result": None,
        "error": None,
    })

    manager_core.FirmwareManager(
        manager_core.ProviderRegistry(
            provider_dir="/nonexistent", builtins=[FakeProvider("system")]),
        task_store=store,
    )

    task = store.read(task_id)
    assert task["state"] == "failed"
    assert task["phase"] == "interrupted"
    assert task["error"]["code"] == "manager-interrupted"
