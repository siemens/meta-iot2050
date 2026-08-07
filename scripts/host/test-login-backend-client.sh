#!/bin/bash
#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." >/dev/null 2>&1 && pwd)"
CLIENT="${REPO_ROOT}/meta/recipes-core/iot2050-login-security/files/login-backend-client.py"
TEST_DIR="$(mktemp -d)"
SOCKET_PATH="${TEST_DIR}/backend.sock"
READY_PATH="${TEST_DIR}/ready"
SERVER_PID=""

cleanup() {
    if [[ -n "${SERVER_PID}" ]]; then
        kill "${SERVER_PID}" 2>/dev/null || true
        wait "${SERVER_PID}" 2>/dev/null || true
    fi
    rm -rf "${TEST_DIR}"
}
trap cleanup EXIT

python3 - "${SOCKET_PATH}" "${READY_PATH}" <<'PY' &
import json
import socket
import sys

path = sys.argv[1]
ready_path = sys.argv[2]
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(path)
server.listen(1)
with open(ready_path, "w", encoding="ascii"):
    pass
connection, _ = server.accept()
data = connection.recv(4096)
request = json.loads(data.decode().split("\n", 1)[0])
assert request == {"action": "failed-login/status", "target": "nobody"}
connection.sendall((json.dumps({
    "tool": "iot2050-login-backend",
    "action": "failed-login/status",
    "target": "nobody",
    "result": "success",
    "reason": "status",
    "error_code": "OK",
    "exit_code": 0,
    "detail": "Failed-login state queried",
    "faillock_output": "nobody:",
}) + "\n").encode())
connection.close()
server.close()
PY
SERVER_PID=$!

ready_deadline=$((SECONDS + 5))
while [[ ! -e "${READY_PATH}" ]]; do
    if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
        echo '[FAIL] Backend protocol test server exited before becoming ready' >&2
        exit 1
    fi
    if (( SECONDS >= ready_deadline )); then
        echo '[FAIL] Backend protocol test server did not become ready within 5 seconds' >&2
        exit 1
    fi
done

if [[ ! -S "${SOCKET_PATH}" ]]; then
    echo '[FAIL] Backend protocol test server did not become ready' >&2
    exit 1
fi

output="$(IOT2050_LOGIN_BACKEND_SOCKET="${SOCKET_PATH}" python3 "${CLIENT}" --format json failed-login status nobody)"
python3 - "${output}" <<'PY'
import json
import sys
payload = json.loads(sys.argv[1])
assert payload["result"] == "success"
assert payload["error_code"] == "OK"
assert payload["exit_code"] == 0
PY
wait "${SERVER_PID}"
printf '%s\n' '[PASS] Login backend client JSON protocol check'
