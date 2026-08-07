#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#

import json
import grp
import logging
import os
import pwd
import re
import socket
import struct
import subprocess
from pathlib import Path

SOCKET_PATH = "/run/iot2050/login-backend.sock"
ADMIN_GROUP = "iot2050-admin"
MAX_REQUEST_BYTES = 4096
PASSWORD_MIN_LENGTH = 12
VALID_ACTIONS = {
    "failed-login/status",
    "failed-login/reset",
    "account/set-password",
    "account/unlock",
    "account/status",
    "account/disable",
    "account/enable",
    "account/delete",
}
ERROR_CODES = {
    "invalid-request": (2, "E_INVALID_REQUEST"),
    "privilege-required": (10, "E_PRIVILEGE_REQUIRED"),
    "invalid-user": (11, "E_INVALID_USER"),
    "unknown-user": (12, "E_UNKNOWN_USER"),
    "protected-root": (13, "E_PROTECTED_ROOT"),
    "protected-system-user": (14, "E_PROTECTED_SYSTEM_USER"),
    "protected-service-user": (15, "E_PROTECTED_SERVICE_USER"),
    "helper-failed": (20, "E_HELPER_FAILED"),
    "password-policy": (21, "E_PASSWORD_UPDATE_FAILED"),
    "last-admin-protected": (23, "E_LAST_ADMIN_PROTECTED"),
    "account-operation-failed": (24, "E_ACCOUNT_OPERATION_FAILED"),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
LOG = logging.getLogger("iot2050-login-backend")


def response(action, target, result, reason, error_code, exit_code, detail, **extra):
    payload = {
        "tool": "iot2050-login-backend",
        "action": action,
        "target": target,
        "result": result,
        "reason": reason,
        "error_code": error_code,
        "exit_code": exit_code,
        "detail": detail,
    }
    payload.update(extra)
    return payload


def error(action, target, reason, detail):
    exit_code, error_code = ERROR_CODES[reason]
    LOG.info(
        "action=%s target=%s result=denied reason=%s actor_uid=%s",
        action,
        target,
        reason,
        os.getuid(),
    )
    return response(action, target, "denied", reason, error_code, exit_code, detail)


def peer_uid(connection):
    credentials = connection.getsockopt(
        socket.SOL_SOCKET,
        socket.SO_PEERCRED,
        struct.calcsize("3i"),
    )
    _, uid, _ = struct.unpack("3i", credentials)
    return uid


def is_authorized(uid):
    if uid == 0:
        return True
    try:
        account = pwd.getpwuid(uid)
    except KeyError:
        return False
    try:
        admin_gid = grp.getgrnam(ADMIN_GROUP).gr_gid
    except KeyError:
        return False
    try:
        return admin_gid in os.getgrouplist(account.pw_name, account.pw_gid)
    except OSError:
        return False


def valid_target(target):
    if not target or not all(character.isalnum() or character in "._-" for character in target):
        return "invalid-user", "Invalid user name"
    if target == "root":
        return "protected-root", "Root operations are not available through this backend"
    try:
        account = pwd.getpwnam(target)
    except KeyError:
        return "unknown-user", "Unknown user"
    if account.pw_uid < 1000:
        return "protected-system-user", "System accounts are protected"
    return None, None


def usable_admins():
    try:
        admin_gid = grp.getgrnam(ADMIN_GROUP).gr_gid
    except KeyError:
        return []

    accounts = []
    for account in pwd.getpwall():
        if account.pw_uid < 1000 or account.pw_shell.endswith(("/nologin", "/false")):
            continue
        try:
            groups = os.getgrouplist(account.pw_name, account.pw_gid)
        except OSError:
            continue
        if admin_gid not in groups:
            continue
        if account.pw_passwd.startswith("!") or account.pw_passwd.startswith("*"):
            continue
        accounts.append(account.pw_name)
    return accounts


def account_status(action, target, actor_uid):
    account = pwd.getpwnam(target)
    locked = account.pw_passwd.startswith(("!", "*"))
    return response(
        action,
        target,
        "success",
        "status",
        "OK",
        0,
        "Account status queried",
        actor_uid=actor_uid,
        uid=account.pw_uid,
        shell=account.pw_shell,
        locked=locked,
        admin=target in usable_admins(),
    )


def account_lifecycle(action, target, actor_uid):
    current_admins = usable_admins()
    if action in {"account/disable", "account/delete"} and target in current_admins and len(current_admins) <= 1:
        return error(action, target, "last-admin-protected", "The last usable administrator cannot be disabled or deleted")

    commands = {
        "account/disable": ["usermod", "--lock", "--shell", "/usr/sbin/nologin", target],
        "account/enable": ["usermod", "--unlock", "--shell", "/bin/bash", target],
        "account/delete": ["userdel", "--remove", target],
    }
    try:
        completed = subprocess.run(
            commands[action],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return error(action, target, "account-operation-failed", str(exc))
    if completed.returncode != 0:
        return error(action, target, "account-operation-failed", "Account operation failed")
    LOG.info(
        "action=%s target=%s result=success reason=account-updated actor_uid=%s",
        action,
        target,
        actor_uid,
    )
    return response(action, target, "success", "account-updated", "OK", 0, "Account updated", actor_uid=actor_uid)


def password_policy_error(password):
    if len(password) < PASSWORD_MIN_LENGTH:
        return "Password must be at least 12 characters"

    classes = sum(
        bool(pattern.search(password))
        for pattern in (
            re.compile(r"[a-z]"),
            re.compile(r"[A-Z]"),
            re.compile(r"[0-9]"),
            re.compile(r"[^A-Za-z0-9]"),
        )
    )
    if classes < 3:
        return "Password must contain at least 3 character classes"
    if re.search(r"(.)\1\1\1", password):
        return "Password must not contain 4 repeated characters"
    if re.search(r"0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210", password):
        return "Password must not contain simple sequences"
    return None


def dispatch(request, actor_uid):
    if not isinstance(request, dict):
        return error("unknown", "", "invalid-request", "Request must be a JSON object")

    action = request.get("action", "")
    target = request.get("target", "")
    if not isinstance(action, str) or action not in VALID_ACTIONS:
        return error(str(action), str(target), "invalid-request", "Unsupported action")
    if not isinstance(target, str):
        return error(action, "", "invalid-request", "Target must be a string")

    if not is_authorized(actor_uid):
        return error(action, target, "privilege-required", "Caller is not an iot2050-admin")

    reason, detail = valid_target(target)
    if reason:
        return error(action, target, reason, detail)

    if action == "account/set-password":
        password = request.get("password")
        if not isinstance(password, str) or "\n" in password or "\r" in password or ":" in password:
            return error(action, target, "password-policy", "Password contains unsupported characters")
        policy_error = password_policy_error(password)
        if policy_error:
            return error(action, target, "password-policy", policy_error)
        return reset_password(action, target, password, actor_uid)

    if action == "account/status":
        return account_status(action, target, actor_uid)

    if action in {"account/disable", "account/enable", "account/delete"}:
        return account_lifecycle(action, target, actor_uid)

    domain, operation = action.split("/", 1)
    helper = "/usr/sbin/iot2050-failed-login" if domain == "failed-login" else "/usr/sbin/iot2050-account-admin"
    command = [helper, "--format", "json", operation, target]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return error(action, target, "helper-failed", str(exc))

    try:
        helper_payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return error(action, target, "helper-failed", "Helper returned invalid JSON")

    helper_payload["tool"] = "iot2050-login-backend"
    helper_payload["actor_uid"] = actor_uid
    LOG.info(
        "action=%s target=%s result=%s reason=%s actor_uid=%s",
        action,
        target,
        helper_payload.get("result", "unknown"),
        helper_payload.get("reason", "unknown"),
        actor_uid,
    )
    return helper_payload


def reset_password(action, target, password, actor_uid):
    try:
        completed = subprocess.run(
            ["chpasswd"],
            input=f"{target}:{password}\n",
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return error(action, target, "helper-failed", str(exc))

    if completed.returncode != 0:
        return error(action, target, "helper-failed", "Password update failed")

    reset = subprocess.run(
        ["faillock", "--user", target, "--reset"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if reset.returncode != 0:
        return error(action, target, "helper-failed", "Password updated but failed-login state was not cleared")

    LOG.info(
        "action=%s target=%s result=success reason=password-reset-and-unlock actor_uid=%s",
        action,
        target,
        actor_uid,
    )
    return response(
        action,
        target,
        "success",
        "password-reset-and-unlock",
        "OK",
        0,
        "Password updated and failed-login state cleared",
        actor_uid=actor_uid,
    )


def serve_connection(connection):
    with connection:
        actor_uid = peer_uid(connection)
        chunks = []
        size = 0
        while size <= MAX_REQUEST_BYTES:
            chunk = connection.recv(min(1024, MAX_REQUEST_BYTES + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if b"\n" in chunk:
                break
        request_data = b"".join(chunks).split(b"\n", 1)[0]
        if len(request_data) > MAX_REQUEST_BYTES:
            payload = error("unknown", "", "invalid-request", "Request is too large")
        else:
            try:
                request = json.loads(request_data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                request = None
            payload = dispatch(request, actor_uid)
        connection.sendall((json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8"))


def main():
    listen_fds = int(os.environ.get("LISTEN_FDS", "0"))
    listen_pid = int(os.environ.get("LISTEN_PID", "0"))
    if listen_fds == 1 and listen_pid == os.getpid():
        server = socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        Path(SOCKET_PATH).parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        os.chmod(SOCKET_PATH, 0o660)
    try:
        while True:
            connection, _ = server.accept()
            serve_connection(connection)
    finally:
        server.close()
        try:
            os.unlink(SOCKET_PATH)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
