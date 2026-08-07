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
snapshot_file="scripts/host/login-admin-schema-snapshots.txt"

fail() {
    echo "[FAIL] $1" >&2
    exit 1
}

pass() {
    echo "[PASS] $1"
}

expected_hash() {
    key_value="$1"
    awk -v key="${key_value}" '$1 == key {print $2}' "${snapshot_file}"
}

actual_hash() {
    output_value="$1"
    printf '%s' "${output_value}" | sha256sum | awk '{print $1}'
}

check_snapshot() {
    key_value="$1"
    command_label="$2"
    output_value="$3"

    expected_value="$(expected_hash "${key_value}")"
    [ -n "${expected_value}" ] || fail "Missing snapshot key: ${key_value}"

    actual_value="$(actual_hash "${output_value}")"
    [ "${actual_value}" = "${expected_value}" ] || fail "Schema snapshot mismatch for ${command_label}: expected ${expected_value}, got ${actual_value}"

    pass "Schema snapshot matches for ${command_label}"
}

schema_text_full="$(sh "${login_admin_helper}" schema)"
schema_id_text_full="$(sh "${login_admin_helper}" schema-id)"
schema_text_failed_login_status="$(sh "${login_admin_helper}" schema failed-login/status)"
schema_id_text_failed_login_status="$(sh "${login_admin_helper}" schema-id failed-login/status)"
schema_json_full="$(sh "${login_admin_helper}" --format json schema)"
schema_id_json_full="$(sh "${login_admin_helper}" --format json schema-id)"
schema_json_account_unlock="$(sh "${login_admin_helper}" --format json schema account/unlock)"
schema_id_json_account_unlock="$(sh "${login_admin_helper}" --format json schema-id account/unlock)"

check_snapshot "schema_text_full" "schema" "${schema_text_full}"
check_snapshot "schema_id_text_full" "schema-id" "${schema_id_text_full}"
check_snapshot "schema_text_failed_login_status" "schema failed-login/status" "${schema_text_failed_login_status}"
check_snapshot "schema_id_text_failed_login_status" "schema-id failed-login/status" "${schema_id_text_failed_login_status}"
check_snapshot "schema_json_full" "--format json schema" "${schema_json_full}"
check_snapshot "schema_id_json_full" "--format json schema-id" "${schema_id_json_full}"
check_snapshot "schema_json_account_unlock" "--format json schema account/unlock" "${schema_json_account_unlock}"
check_snapshot "schema_id_json_account_unlock" "--format json schema-id account/unlock" "${schema_id_json_account_unlock}"

echo "[PASS] Login-admin schema snapshot checks completed"
