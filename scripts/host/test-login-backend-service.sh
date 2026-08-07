#!/bin/bash
#
# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." >/dev/null 2>&1 && pwd)"
SERVICE="${REPO_ROOT}/meta/recipes-core/iot2050-login-security/files/login-backend-service.py"

PYTHONDONTWRITEBYTECODE=1 /bin/python3 - "${SERVICE}" <<'PY'
import importlib.util
import subprocess
import sys
from types import SimpleNamespace

service_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("login_backend_service", service_path)
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)

accounts = {}
admin_names = set()


def account(name, uid=1000, shell="/bin/bash", passwd="x"):
    return SimpleNamespace(
        pw_name=name,
        pw_uid=uid,
        pw_gid=uid,
        pw_shell=shell,
        pw_passwd=passwd,
    )


def configure_accounts(*names):
    global accounts, admin_names
    accounts = {name: account(name, 1000 + index) for index, name in enumerate(names)}
    admin_names = set(names)
    service.pwd.getpwall = lambda: list(accounts.values())
    service.pwd.getpwnam = lambda name: accounts[name]
    service.grp.getgrnam = lambda name: SimpleNamespace(gr_gid=4242)
    service.os.getgrouplist = lambda name, gid: [4242] if name in admin_names else []


def assert_error(payload, error_code, exit_code):
    assert payload["result"] == "denied", payload
    assert payload["error_code"] == error_code, payload
    assert payload["exit_code"] == exit_code, payload


configure_accounts("alice")
service.subprocess.run = lambda *args, **kwargs: (_ for _ in ()).throw(
    AssertionError("last-admin protection must not invoke a system command")
)
assert_error(
    service.account_lifecycle("account/disable", "alice", 0),
    "E_LAST_ADMIN_PROTECTED",
    23,
)
assert_error(
    service.account_lifecycle("account/delete", "alice", 0),
    "E_LAST_ADMIN_PROTECTED",
    23,
)

configure_accounts("alice", "bob")
commands = []
service.subprocess.run = lambda command, **kwargs: (
    commands.append(command) or subprocess.CompletedProcess(command, 0, "", "")
)
payload = service.account_lifecycle("account/disable", "alice", 0)
assert payload["error_code"] == "OK", payload
assert commands == [["usermod", "--lock", "--shell", "/usr/sbin/nologin", "alice"]], commands

service.is_authorized = lambda uid: False
assert_error(
    service.dispatch({"action": "account/status", "target": "alice"}, 1001),
    "E_PRIVILEGE_REQUIRED",
    10,
)

service.is_authorized = lambda uid: True
configure_accounts("alice")
assert_error(
    service.dispatch({"action": "account/status", "target": "root"}, 0),
    "E_PROTECTED_ROOT",
    13,
)
assert_error(
    service.dispatch({"action": "account/set-password", "target": "alice", "password": "short"}, 0),
    "E_PASSWORD_UPDATE_FAILED",
    21,
)
assert service.valid_target("bad/name")[0] == "invalid-user"
assert service.valid_target("missing")[0] == "unknown-user"

print("[PASS] Login backend service authorization, lifecycle, and password-policy checks")
PY
