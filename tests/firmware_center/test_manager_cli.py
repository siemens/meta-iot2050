# SPDX-License-Identifier: MIT

import json

import pytest

from conftest import REPO_ROOT, load_source


MANAGER_CLI = REPO_ROOT / "meta-example/recipes-app/iot2050-firmware-manager/files/iot2050-fwmgr"


@pytest.fixture
def manager_cli():
    return load_source("firmware_manager_cli_under_test", MANAGER_CLI)


def test_capabilities_command_emits_manager_response(manager_cli, monkeypatch, capsys):
    requests = []

    def fake_request(request, socket_path):
        requests.append(request)
        return {"v": 1, "id": request["id"], "ok": True, "data": []}

    monkeypatch.setattr(manager_cli, "request_manager", fake_request)

    assert manager_cli.main(["capabilities"]) == 0
    assert requests[0]["op"] == "capabilities.list"
    assert json.loads(capsys.readouterr().out)["ok"] is True


def test_inspect_passes_provider_and_payload(manager_cli, monkeypatch):
    requests = []

    def fake_request(request, socket_path):
        requests.append(request)
        return {"v": 1, "id": request["id"], "ok": True, "data": {}}

    monkeypatch.setattr(manager_cli, "request_manager", fake_request)

    assert manager_cli.main([
        "inspect", "module", "--payload", '{"slot":2}'
    ]) == 0
    assert requests[0]["provider"] == "module"
    assert requests[0]["payload"] == {"slot": 2}


def test_manager_error_response_returns_failure(manager_cli, monkeypatch, capsys):
    monkeypatch.setattr(manager_cli, "request_manager", lambda *args: {
        "v": 1,
        "id": "request",
        "ok": False,
        "error": {"code": "provider-unavailable", "message": "unavailable"},
    })

    assert manager_cli.main(["inspect", "controller"]) == 1
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "provider-unavailable"