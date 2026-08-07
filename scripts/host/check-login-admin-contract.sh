#!/bin/sh

#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#

set -eu

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." >/dev/null 2>&1 && pwd)"

cd "${REPO_ROOT}"

login_admin_helper="meta/recipes-core/iot2050-login-security/files/iot2050-login-admin"
login_backend_service="meta/recipes-core/iot2050-login-security/files/login-backend-service.py"
login_backend_client="meta/recipes-core/iot2050-login-security/files/login-backend-client.py"
login_backend_client_test="scripts/host/test-login-backend-client.sh"
login_backend_service_test="scripts/host/test-login-backend-service.sh"

fail() {
    echo "[FAIL] $1" >&2
    exit 1
}

pass() {
    echo "[PASS] $1"
}

contains_text() {
    printf '%s\n' "$1" | grep -F -q "$2"
}

run_helper() {
    sh "${login_admin_helper}" "$@"
}

check_action_contract() {
    action_key="$1"
    expected_optional_text="$2"
    expected_optional_json="$3"

    schema_text="$(run_helper schema "${action_key}")"
    schema_json="$(run_helper --format json schema "${action_key}")"
    schema_id_text="$(run_helper schema-id "${action_key}")"
    schema_id_json="$(run_helper --format json schema-id "${action_key}")"

    contains_text "${schema_text}" "action=${action_key}" || fail "Action schema text must include ${action_key}"
    contains_text "${schema_json}" "\"action\":\"${action_key}\"" || fail "Action schema JSON must include ${action_key}"

    expected_contract_id="iot2050-login-admin/1.0.0/${action_key}"
    contains_text "${schema_text}" "contract_id=${expected_contract_id}" || fail "Action schema text must expose ${expected_contract_id}"
    contains_text "${schema_json}" "\"contract_id\":\"${expected_contract_id}\"" || fail "Action schema JSON must expose ${expected_contract_id}"
    contains_text "${schema_id_text}" "contract_id=${expected_contract_id}" || fail "Action schema-id text must expose ${expected_contract_id}"
    contains_text "${schema_id_json}" "\"contract_id\":\"${expected_contract_id}\"" || fail "Action schema-id JSON must expose ${expected_contract_id}"

    contains_text "${schema_text}" "optional=${expected_optional_text}" || fail "Action schema text optional fields mismatch for ${action_key}"
    contains_text "${schema_json}" "\"optional_fields\":${expected_optional_json}" || fail "Action schema JSON optional fields mismatch for ${action_key}"

    pass "Action contract is self-consistent for ${action_key}"
}

schema_id_full_text="$(run_helper schema-id)"
contains_text "${schema_id_full_text}" 'contract_id=iot2050-login-admin/1.0.0/full' || fail "Full schema-id text output must expose full contract_id"
pass "Full schema-id text output exposes full contract_id"

schema_id_full_json="$(run_helper --format json schema-id)"
contains_text "${schema_id_full_json}" '"contract_id":"iot2050-login-admin/1.0.0/full"' || fail "Full schema-id JSON output must expose full contract_id"
pass "Full schema-id JSON output exposes full contract_id"

check_action_contract "failed-login/status" "none" "[]"
check_action_contract "failed-login/reset" "faillock_output" '["faillock_output"]'
check_action_contract "account/set-password" "faillock_output" '["faillock_output"]'
check_action_contract "account/unlock" "faillock_output" '["faillock_output"]'
check_action_contract "account/status" "faillock_output" '["faillock_output"]'
check_action_contract "account/disable" "faillock_output" '["faillock_output"]'
check_action_contract "account/enable" "faillock_output" '["faillock_output"]'
check_action_contract "account/delete" "faillock_output" '["faillock_output"]'

set +e
invalid_schema_out="$(run_helper schema invalid/domain 2>&1)"
invalid_schema_status=$?
invalid_schema_id_out="$(run_helper schema-id invalid/domain 2>&1)"
invalid_schema_id_status=$?
set -e

[ "${invalid_schema_status}" -eq 2 ] || fail "Invalid schema action must return usage-compatible exit code 2"
contains_text "${invalid_schema_out}" 'Unknown schema action: invalid/domain' || fail "Invalid schema action must print a clear rejection reason"
[ "${invalid_schema_id_status}" -eq 2 ] || fail "Invalid schema-id action must return usage-compatible exit code 2"
contains_text "${invalid_schema_id_out}" 'Unknown schema action: invalid/domain' || fail "Invalid schema-id action must print a clear rejection reason"
pass "Invalid schema and schema-id actions return stable error contract"

set +e
backend_out="$(IOT2050_LOGIN_BACKEND_SOCKET=/run/iot2050/contract-test-missing.sock python3 "${login_backend_client}" failed-login status test-user 2>&1)"
backend_status=$?
set -e
[ "${backend_status}" -eq 20 ] || fail "Unavailable backend client must return exit code 20"
contains_text "${backend_out}" 'E_BACKEND_UNAVAILABLE' || fail "Unavailable backend client must expose E_BACKEND_UNAVAILABLE"
pass "Backend client reports unavailable socket with stable contract"

if command -v faillock >/dev/null 2>&1 && [ "$(id -u)" -eq 0 ]; then
    json_status_out="$(sh "meta/recipes-core/iot2050-login-security/files/iot2050-failed-login" --format json status nobody 2>/dev/null || true)"
    json_line_count="$(printf '%s\n' "${json_status_out}" | grep -c '^{' || true)"
    [ "${json_line_count}" -eq 1 ] || fail "JSON failed-login status must emit one JSON object"
    pass "JSON failed-login status emits one machine-readable object"
fi

contains_text "$(cat "${login_backend_service}")" 'SO_PEERCRED' || fail "Backend service must use peer credentials"
contains_text "$(cat "${login_backend_service}")" 'iot2050-admin' || fail "Backend service must enforce iot2050-admin authorization"
contains_text "$(cat "${login_backend_service}")" 'chpasswd' || fail "Backend service must use chpasswd for password reset"
contains_text "$(cat "${login_backend_service}")" 'faillock' || fail "Backend service must clear faillock after password reset"
pass "Backend service source contains authorization and recovery controls"

if [ -x "${login_backend_client_test}" ]; then
    bash "${login_backend_client_test}"
    pass "Backend client socket protocol test passes"
fi

if [ -x "${login_backend_service_test}" ]; then
    bash "${login_backend_service_test}"
    pass "Backend service authorization and lifecycle test passes"
fi

echo "[PASS] Login-admin schema contract dynamic checks completed"
