#!/usr/bin/env bash

#
# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT
#

set -euo pipefail

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    color_reset=$'\033[0m'
    color_info=$'\033[36m'
    color_pass=$'\033[32m'
    color_fail=$'\033[31m'
else
    color_reset=""
    color_info=""
    color_pass=""
    color_fail=""
fi

info() {
    printf '%s[INFO]%s %s\n' "${color_info}" "${color_reset}" "$*"
}

pass() {
    printf '%s[PASS]%s %s\n' "${color_pass}" "${color_reset}" "$*"
}

fail() {
    printf '%s[FAIL]%s %s\n' "${color_fail}" "${color_reset}" "$*" >&2
}

usage() {
    cat <<'EOF'
Usage: check-login-runtime-remote.sh [OPTIONS]

Interactive runtime diagnostic for IOT2050 login security.
Without --password, you will be prompted for SSH and sudo passwords.

Options:
    --host HOST             Target host/IP (default: 192.168.200.1)
    --user USER             SSH user (default: iot2050)
    --port PORT             SSH port (default: 22)
    --password PASSWORD     Use PASSWORD for SSH and sudo authentication.
                                                    Quote it in the shell when it contains special characters.
    --lifecycle-user USER   Read-only account status probe for USER.
    --lifecycle-test-user USER
                                                    Create and fully exercise a temporary USER, then remove it.
                                                    USER must start with iot2050-rt-.
    -h, --help              Show this help
EOF
}

HOST="192.168.200.1"
USER="iot2050"
PORT="22"
PASSWORD=""
PASSWORD_SET="0"
LIFECYCLE_USER=""
LIFECYCLE_USER_SET="0"
LIFECYCLE_TEST_USER=""
LIFECYCLE_TEST_USER_SET="0"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --host)
            HOST="${2:-}"
            shift 2
            ;;
        --user)
            USER="${2:-}"
            shift 2
            ;;
        --port)
            PORT="${2:-}"
            shift 2
            ;;
        --password)
            if [ "$#" -lt 2 ]; then
                echo "--password requires a value" >&2
                exit 2
            fi
            PASSWORD="$2"
            PASSWORD_SET="1"
            shift 2
            ;;
        --password=*)
            PASSWORD="${1#*=}"
            PASSWORD_SET="1"
            shift
            ;;
        --lifecycle-user)
            if [ "$#" -lt 2 ]; then
                echo "--lifecycle-user requires a value" >&2
                exit 2
            fi
            LIFECYCLE_USER="$2"
            LIFECYCLE_USER_SET="1"
            shift 2
            ;;
        --lifecycle-user=*)
            LIFECYCLE_USER="${1#*=}"
            LIFECYCLE_USER_SET="1"
            shift
            ;;
        --lifecycle-test-user)
            if [ "$#" -lt 2 ]; then
                echo "--lifecycle-test-user requires a value" >&2
                exit 2
            fi
            LIFECYCLE_TEST_USER="$2"
            LIFECYCLE_TEST_USER_SET="1"
            shift 2
            ;;
        --lifecycle-test-user=*)
            LIFECYCLE_TEST_USER="${1#*=}"
            LIFECYCLE_TEST_USER_SET="1"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [ -z "${HOST}" ] || [ -z "${USER}" ] || [ -z "${PORT}" ]; then
    echo "host/user/port cannot be empty" >&2
    exit 2
fi

if [ "${LIFECYCLE_USER_SET}" = "1" ] &&
    [[ ! "${LIFECYCLE_USER}" =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "lifecycle user must be a simple local account name" >&2
    exit 2
fi

if [ "${LIFECYCLE_TEST_USER_SET}" = "1" ] &&
    [[ ! "${LIFECYCLE_TEST_USER}" =~ ^iot2050-rt-[a-z0-9._-]+$ ]]; then
    echo "lifecycle test user must match iot2050-rt-<name>" >&2
    exit 2
fi

info "Target: ${USER}@${HOST}:${PORT}"
info "Using one SSH session for authentication and diagnostics."

tmp_out="$(mktemp)"
remote_script="$(mktemp)"
trap 'rm -f "${tmp_out}" "${remote_script}"' EXIT INT TERM

printf "LIFECYCLE_USER='%s'\nLIFECYCLE_TEST_USER='%s'\n" \
    "${LIFECYCLE_USER}" "${LIFECYCLE_TEST_USER}" >"${remote_script}"
cat >>"${remote_script}" <<'REMOTE_SCRIPT'
set -euo pipefail

echo "__BEGIN_RUNTIME_DIAG__"

echo "R_GROUP=$(if getent group iot2050-admin >/dev/null; then echo present; else echo missing; fi)"

echo "R_SOCKET_ENABLED=$(systemctl is-enabled iot2050-login-backend.socket 2>/dev/null || true)"
echo "R_SOCKET_ACTIVE=$(systemctl is-active iot2050-login-backend.socket 2>/dev/null || true)"

socket_status="$(systemctl --no-pager --full status iot2050-login-backend.socket 2>&1 || true)"
if printf "%s\n" "${socket_status}" | grep -q "Failed to resolve group iot2050-admin"; then
    echo "R_SOCKET_GROUP_ERROR=yes"
else
    echo "R_SOCKET_GROUP_ERROR=no"
fi

service_status="$(systemctl --no-pager --full status iot2050-login-backend.service 2>&1 || true)"
if printf "%s\n" "${service_status}" | grep -q "dependency"; then
    echo "R_SERVICE_DEPENDENCY_ERROR=yes"
else
    echo "R_SERVICE_DEPENDENCY_ERROR=no"
fi

echo "R_PERMIT_ROOT_LOGIN=$(sshd -T 2>/dev/null | awk '/^permitrootlogin / {print $2; exit}' || true)"

echo "R_FAILLOCK_DIR_CONF=$(if grep -q '^dir=/var/lib/faillock$' /etc/security/faillock.conf 2>/dev/null; then echo present; else echo missing; fi)"
echo "R_FAILLOCK_DIR_EXISTS=$(if [ -d /var/lib/faillock ]; then echo present; else echo missing; fi)"
echo "R_CRACKLIB_DICT_EXISTS=$(if [ -f /var/cache/cracklib/cracklib_dict.pwd ]; then echo present; else echo missing; fi)"

echo "R_BACKEND_CMD=$(if command -v iot2050-login-backend >/dev/null 2>&1 || [ -x /usr/sbin/iot2050-login-backend ]; then echo present; else echo missing; fi)"
backend_output="$(/usr/sbin/iot2050-login-backend --format json account status root 2>&1 || true)"
backend_error_code="$(printf "%s\n" "${backend_output}" | sed -n 's/.*"error_code":"\([^"]*\)".*/\1/p' | head -n 1)"
echo "R_BACKEND_ERROR_CODE=${backend_error_code:-unknown}"
if [ "${backend_error_code}" = "E_PROTECTED_ROOT" ]; then
    echo "R_BACKEND_SMOKE=ok"
elif [ "${backend_error_code}" = "E_BACKEND_UNAVAILABLE" ]; then
    echo "R_BACKEND_SMOKE=unavailable"
else
    echo "R_BACKEND_SMOKE=fail"
fi

echo "__SSH_DROPINS_BEGIN__"
ls -1 /etc/ssh/sshd_config.d/*.conf 2>/dev/null || true
echo "__SSH_DROPINS_END__"

echo "__SOCKET_STATUS_BEGIN__"
printf "%s\n" "${socket_status}"
echo "__SOCKET_STATUS_END__"

echo "__SERVICE_STATUS_BEGIN__"
printf "%s\n" "${service_status}"
echo "__SERVICE_STATUS_END__"

if [ -n "${LIFECYCLE_USER}" ]; then
    echo "R_LIFECYCLE_USER=${LIFECYCLE_USER}"
    lifecycle_output="$(/usr/sbin/iot2050-login-backend --format json account status "${LIFECYCLE_USER}" 2>&1 || true)"
    lifecycle_error_code="$(printf "%s\n" "${lifecycle_output}" | sed -n 's/.*"error_code":"\([^"]*\)".*/\1/p' | head -n 1)"
    echo "R_LIFECYCLE_ERROR_CODE=${lifecycle_error_code:-unknown}"
    if [ "${lifecycle_error_code}" = "OK" ]; then
        echo "R_LIFECYCLE_STATUS=ok"
    else
        echo "R_LIFECYCLE_STATUS=fail"
    fi
fi

if [ -n "${LIFECYCLE_TEST_USER}" ]; then
    lifecycle_test_failures=0
    lifecycle_test_password='Aq7!xY9#kL2@pR5$'

    cleanup_lifecycle_test_user() {
        userdel --remove "${LIFECYCLE_TEST_USER}" >/dev/null 2>&1 || true
    }
    trap cleanup_lifecycle_test_user EXIT

    if getent passwd "${LIFECYCLE_TEST_USER}" >/dev/null 2>&1; then
        echo "R_LIFECYCLE_TEST_STATUS=fail"
        echo "R_LIFECYCLE_TEST_ERROR=account-already-exists"
        exit 1
    fi

    if ! useradd --create-home --shell /bin/bash "${LIFECYCLE_TEST_USER}"; then
        echo "R_LIFECYCLE_TEST_STATUS=fail"
        echo "R_LIFECYCLE_TEST_ERROR=user-create-failed"
        exit 1
    fi
    printf '%s:%s\n' "${LIFECYCLE_TEST_USER}" "${lifecycle_test_password}" | chpasswd

    lifecycle_test_action() {
        action_name="$1"
        expected_locked="$2"
        action_output="$(/usr/sbin/iot2050-login-backend --format json account "${action_name}" "${LIFECYCLE_TEST_USER}" 2>&1 || true)"
        action_error_code="$(printf '%s\n' "${action_output}" | sed -n 's/.*"error_code":"\([^"]*\)".*/\1/p' | head -n 1)"
        if [ "${action_error_code}" != "OK" ]; then
            echo "R_LIFECYCLE_TEST_${action_name^^}_ERROR=${action_error_code:-unknown}"
            echo "R_LIFECYCLE_TEST_${action_name^^}=fail"
            lifecycle_test_failures=$((lifecycle_test_failures + 1))
            return
        fi

        status_output="$(/usr/sbin/iot2050-login-backend --format json account status "${LIFECYCLE_TEST_USER}" 2>&1 || true)"
        status_error_code="$(printf '%s\n' "${status_output}" | sed -n 's/.*"error_code":"\([^"]*\)".*/\1/p' | head -n 1)"
        status_locked="$(printf '%s\n' "${status_output}" | sed -n 's/.*"locked":\(true\|false\).*/\1/p' | head -n 1)"
        if [ "${status_error_code}" != "OK" ] || [ "${status_locked}" != "${expected_locked}" ]; then
            echo "R_LIFECYCLE_TEST_${action_name^^}_STATUS_ERROR=${status_error_code:-unknown}/${status_locked:-unknown}"
            echo "R_LIFECYCLE_TEST_${action_name^^}=fail"
            lifecycle_test_failures=$((lifecycle_test_failures + 1))
        else
            echo "R_LIFECYCLE_TEST_${action_name^^}=ok"
        fi
    }

    lifecycle_test_action disable true
    lifecycle_test_action enable false

    delete_output="$(/usr/sbin/iot2050-login-backend --format json account delete "${LIFECYCLE_TEST_USER}" 2>&1 || true)"
    delete_error_code="$(printf '%s\n' "${delete_output}" | sed -n 's/.*"error_code":"\([^"]*\)".*/\1/p' | head -n 1)"
    if [ "${delete_error_code}" != "OK" ] || getent passwd "${LIFECYCLE_TEST_USER}" >/dev/null 2>&1; then
        echo "R_LIFECYCLE_TEST_DELETE_ERROR=${delete_error_code:-unknown}"
        echo "R_LIFECYCLE_TEST_DELETE=fail"
        lifecycle_test_failures=$((lifecycle_test_failures + 1))
    else
        echo "R_LIFECYCLE_TEST_DELETE=ok"
    fi

    if [ "${lifecycle_test_failures}" -eq 0 ]; then
        trap - EXIT
        echo "R_LIFECYCLE_TEST_STATUS=ok"
        echo "R_LIFECYCLE_TEST_USER=${LIFECYCLE_TEST_USER}"
    else
        echo "R_LIFECYCLE_TEST_STATUS=fail"
        echo "R_LIFECYCLE_TEST_USER=${LIFECYCLE_TEST_USER}"
        exit 1
    fi
fi

echo "__END_RUNTIME_DIAG__"
REMOTE_SCRIPT

if ! command -v sshpass >/dev/null 2>&1; then
    fail "This checker requires sshpass for non-interactive SSH authentication."
    exit 2
fi

if [ "${PASSWORD_SET}" = "1" ]; then
    ssh_password="${PASSWORD}"
    sudo_password="${PASSWORD}"
else
    if [ ! -r /dev/tty ]; then
        fail "An interactive terminal is required for passwords."
        exit 2
    fi

    printf '%s[INFO]%s SSH password for %s: ' "${color_info}" "${color_reset}" "${USER}" >&2
    IFS= read -r -s ssh_password </dev/tty || {
        printf '\n' >&2
        fail "Could not read SSH password from /dev/tty."
        exit 2
    }
    printf '\n' >&2
    printf '%s[INFO]%s Sudo password for %s: ' "${color_info}" "${color_reset}" "${USER}" >&2
    IFS= read -r -s sudo_password </dev/tty || {
        printf '\n' >&2
        fail "Could not read sudo password from /dev/tty."
        exit 2
    }
    printf '\n' >&2

fi

if [ -z "${sudo_password}" ]; then
    fail "Password is empty."
    exit 2
fi

set +e
{
    printf '%s\n' "${sudo_password}"
    cat "${remote_script}"
} | SSHPASS="${ssh_password}" sshpass -e ssh \
    -T \
    -p "${PORT}" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${USER}@${HOST}" \
    'sudo -S -p "" bash -s' | tee "${tmp_out}"
pipeline_status=("${PIPESTATUS[@]}")
unset ssh_password sudo_password
set -e

ssh_exit="${pipeline_status[1]}"

if [ "${ssh_exit}" -ne 0 ]; then
    fail "Remote command failed with exit ${ssh_exit}"
    info "Check the SSH password and the sudo password entered at the prompts." >&2
    exit "${ssh_exit}"
fi

get_value() {
    local key="$1"
    local line
    line="$(grep -E "^${key}=" "${tmp_out}" | tail -n1 || true)"
    echo "${line#*=}"
}

failures=0

check_equals() {
    local key="$1"
    local expected="$2"
    local actual
    actual="$(get_value "${key}")"
    if [ "${actual}" = "${expected}" ]; then
        pass "${key}=${actual}"
    else
        fail "${key} expected ${expected}, got ${actual:-<empty>}"
        failures=$((failures + 1))
    fi
}

echo
info "Runtime summary"
check_equals "R_GROUP" "present"
check_equals "R_SOCKET_ENABLED" "enabled"
check_equals "R_SOCKET_ACTIVE" "active"
check_equals "R_SOCKET_GROUP_ERROR" "no"
check_equals "R_SERVICE_DEPENDENCY_ERROR" "no"

permit_root_login="$(get_value "R_PERMIT_ROOT_LOGIN")"
if [ "${permit_root_login}" = "yes" ] || [ "${permit_root_login}" = "no" ]; then
    pass "R_PERMIT_ROOT_LOGIN=${permit_root_login}"
else
    fail "R_PERMIT_ROOT_LOGIN expected yes|no, got ${permit_root_login:-<empty>}"
    failures=$((failures + 1))
fi

check_equals "R_FAILLOCK_DIR_CONF" "present"
check_equals "R_FAILLOCK_DIR_EXISTS" "present"
check_equals "R_CRACKLIB_DICT_EXISTS" "present"
check_equals "R_BACKEND_CMD" "present"
backend_smoke="$(get_value "R_BACKEND_SMOKE")"
backend_error_code="$(get_value "R_BACKEND_ERROR_CODE")"
if [ "${backend_smoke}" = "ok" ]; then
    pass "R_BACKEND_SMOKE=ok (${backend_error_code})"
else
    fail "R_BACKEND_SMOKE=${backend_smoke:-unknown} (${backend_error_code:-unknown})"
    failures=$((failures + 1))
fi

if [ "${LIFECYCLE_USER_SET}" = "1" ]; then
    lifecycle_status="$(get_value "R_LIFECYCLE_STATUS")"
    lifecycle_error_code="$(get_value "R_LIFECYCLE_ERROR_CODE")"
    if [ "${lifecycle_status}" = "ok" ]; then
        pass "R_LIFECYCLE_STATUS=ok (${lifecycle_error_code})"
    else
        fail "R_LIFECYCLE_STATUS=${lifecycle_status:-unknown} (${lifecycle_error_code:-unknown})"
        failures=$((failures + 1))
    fi
fi

if [ "${LIFECYCLE_TEST_USER_SET}" = "1" ]; then
    for lifecycle_test_action_name in DISABLE ENABLE DELETE; do
        check_equals "R_LIFECYCLE_TEST_${lifecycle_test_action_name}" "ok"
    done
    lifecycle_test_status="$(get_value "R_LIFECYCLE_TEST_STATUS")"
    lifecycle_test_user="$(get_value "R_LIFECYCLE_TEST_USER")"
    if [ "${lifecycle_test_status}" = "ok" ]; then
        pass "R_LIFECYCLE_TEST_STATUS=ok (${lifecycle_test_user})"
    else
        fail "R_LIFECYCLE_TEST_STATUS=${lifecycle_test_status:-unknown} (${lifecycle_test_user:-unknown})"
        failures=$((failures + 1))
    fi
fi

echo
if [ "${failures}" -eq 0 ]; then
    pass "Runtime login security checks passed"
    exit 0
fi

fail "Runtime login security checks failed (${failures})"
info "Check sections between __SOCKET_STATUS_BEGIN__ and __SERVICE_STATUS_END__ above."
exit 1
