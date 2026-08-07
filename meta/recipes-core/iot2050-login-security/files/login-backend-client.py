#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#

import getpass
import json
import os
import socket
import sys

SOCKET_PATH = os.environ.get("IOT2050_LOGIN_BACKEND_SOCKET", "/run/iot2050/login-backend.sock")
BACKEND_UNAVAILABLE_ERROR = "E_BACKEND_UNAVAILABLE"
MAX_RESPONSE_BYTES = 65536
USAGE = "Usage: iot2050-login-backend [--format text|json] failed-login <status|reset> <user> | account <status|set-password|unlock|disable|enable|delete> <user>"


def usage():
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    output_format = "json"
    arguments = list(argv)
    if len(arguments) >= 2 and arguments[0] == "--format":
        output_format = arguments[1]
        arguments = arguments[2:]
    if output_format not in {"text", "json"} or len(arguments) != 3:
        return usage()

    domain, action, target = arguments
    request = {"action": f"{domain}/{action}", "target": target}
    if request["action"] == "account/set-password":
        try:
            password = getpass.getpass("New password: ")
            confirmation = getpass.getpass("Retype new password: ")
        except (EOFError, KeyboardInterrupt):
            print("Password input cancelled", file=sys.stderr)
            return 2
        if password != confirmation:
            print("Passwords do not match", file=sys.stderr)
            return 2
        request["password"] = password

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(30)
            client.connect(SOCKET_PATH)
            client.sendall((json.dumps(request, separators=(",", ":")) + "\n").encode())
            response = client.recv(MAX_RESPONSE_BYTES)
    except OSError as exc:
        payload = {
            "tool": "iot2050-login-backend",
            "action": request["action"],
            "target": target,
            "result": "denied",
            "reason": "backend-unavailable",
            "error_code": BACKEND_UNAVAILABLE_ERROR,
            "exit_code": 20,
            "detail": str(exc),
        }
        print_result(payload, output_format)
        return 20

    try:
        payload = json.loads(response.decode().split("\n", 1)[0])
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = {
            "tool": "iot2050-login-backend",
            "action": request["action"],
            "target": target,
            "result": "denied",
            "reason": "invalid-response",
            "error_code": "E_INVALID_RESPONSE",
            "exit_code": 20,
            "detail": "Backend returned invalid JSON",
        }

    print_result(payload, output_format)
    return int(payload.get("exit_code", 20))


def print_result(payload, output_format):
    if output_format == "json":
        print(json.dumps(payload, separators=(",", ":")))
        return
    fields = [
        "tool",
        "action",
        "target",
        "result",
        "reason",
        "error_code",
        "exit_code",
        "detail",
    ]
    print(" ".join(f"{field}={payload.get(field, '')}" for field in fields))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
