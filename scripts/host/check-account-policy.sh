#!/bin/sh

#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#

# shellcheck disable=SC2016

set -eu

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." >/dev/null 2>&1 && pwd)"
login_admin_dynamic_checker="${SCRIPT_DIR}/check-login-admin-contract.sh"
login_admin_snapshot_checker="${SCRIPT_DIR}/check-login-admin-schema-snapshot.sh"
login_runtime_remote_checker="${SCRIPT_DIR}/check-login-runtime-remote.sh"

cd "${REPO_ROOT}"

tmp_product="$(mktemp)"
tmp_dev="$(mktemp)"
trap 'rm -f "${tmp_product}" "${tmp_dev}"' EXIT

login_security_template="meta/recipes-core/iot2050-login-security/files/postinst.tmpl"
login_security_recipe="meta/recipes-core/iot2050-login-security/iot2050-login-security_1.0.0.bb"
account_admin_helper="meta/recipes-core/iot2050-login-security/files/iot2050-account-admin"
failed_login_helper="meta/recipes-core/iot2050-login-security/files/iot2050-failed-login"
login_admin_helper="meta/recipes-core/iot2050-login-security/files/iot2050-login-admin"
login_backend_helper="meta/recipes-core/iot2050-login-security/files/iot2050-login-backend"
login_backend_service="meta/recipes-core/iot2050-login-security/files/login-backend-service.py"
login_backend_client="meta/recipes-core/iot2050-login-security/files/login-backend-client.py"
login_backend_service_test="scripts/host/test-login-backend-service.sh"
login_backend_unit="meta/recipes-core/iot2050-login-security/files/iot2050-login-backend.service"
login_backend_socket="meta/recipes-core/iot2050-login-security/files/iot2050-login-backend.socket"
login_security_postinst="meta/recipes-core/iot2050-login-security/files/postinst"
onboarding_user_script="meta-example/recipes-webui/iot2050-firstboot-onboarding/files/iot2050-firstboot-apply-user.py"
onboarding_api_script="meta-example/recipes-webui/iot2050-firstboot-onboarding/files/iot2050-firstboot-onboarding.js"
onboarding_web_script="meta-example/recipes-webui/iot2050-firstboot-onboarding/files/www/app.js"
onboarding_index="meta-example/recipes-webui/iot2050-firstboot-onboarding/files/www/index.html"
dev_root_ssh_postinst="meta/recipes-core/ssh-root-login/files/postinst"
login_admin_snapshot_file="scripts/host/login-admin-schema-snapshots.txt"

./kas-container dump kas-iot2050-example.yml > "${tmp_product}"
./kas-container dump kas-iot2050-example.yml:kas/opt/dev.yml > "${tmp_dev}"

fail() {
    echo "[FAIL] $1" >&2
    exit 1
}

pass() {
    echo "[PASS] $1"
}

contains() {
    grep -F -q -- "$2" "$1"
}

line_number() {
    grep -n -F "$2" "$1" | head -n 1 | cut -d: -f1
}

if contains "${tmp_product}" "USER_root[password]"; then
    fail "Product must not include USER_root[password] in flattened KAS config"
fi
pass "Product has no USER_root[password] in KAS composition"

if contains "${tmp_product}" "USER_iot2050[password]"; then
    fail "Product must not include USER_iot2050[password] in flattened KAS config"
fi
pass "Product has no USER_iot2050[password] in KAS composition"

if contains "${tmp_product}" "IOT2050_DEV_COMPAT_ROOT_SSH = \"1\""; then
    fail "Product must not enable IOT2050_DEV_COMPAT_ROOT_SSH"
fi
pass "Product does not enable dev root SSH switch"

if ! contains "${tmp_product}" "IOT2050_LOCK_ROOT_PASSWORD = \"1\""; then
    fail "Product must keep root password locking enabled by default"
fi
pass "Product keeps root password locking enabled by default"

if ! contains "${tmp_dev}" "USER_root[password] ??= \"root\""; then
    fail "Dev append must include root compatibility password"
fi
pass "Dev append includes root compatibility password"

if ! contains "${tmp_dev}" "USER_iot2050[password] ??= \"iot2050\""; then
    fail "Dev append must include iot2050 compatibility password"
fi
pass "Dev append includes iot2050 compatibility password"

if ! contains "${tmp_dev}" "IOT2050_DEV_COMPAT_ROOT_SSH = \"1\""; then
    fail "Dev append must enable IOT2050_DEV_COMPAT_ROOT_SSH"
fi
pass "Dev append enables dev root SSH switch"

if ! contains "${tmp_dev}" "IOT2050_LOCK_ROOT_PASSWORD = \"0\""; then
    fail "Dev append must disable product root password locking"
fi
pass "Dev append disables product root password locking"

if ! contains "${tmp_product}" "target: iot2050-image-example"; then
    fail "Product target must remain iot2050-image-example"
fi
pass "Product target remains iot2050-image-example"

if ! contains "${login_security_template}" 'pam_faillock.so preauth'; then
    fail "Login security template must configure pam_faillock preauth"
fi
pass "Login security template configures pam_faillock preauth"

if ! contains "${login_security_template}" 'pam_faillock.so authfail'; then
    fail "Login security template must configure pam_faillock authfail"
fi
pass "Login security template configures pam_faillock authfail"

if ! contains "${login_security_template}" 'account required pam_faillock.so'; then
    fail "Login security template must configure pam_faillock account handling"
fi
pass "Login security template configures pam_faillock account handling"

if ! contains "${login_security_template}" 'passwd -l root'; then
    fail "Login security template must lock root when product root lock is enabled"
fi
pass "Login security template locks root when enabled"

if ! contains "${login_security_recipe}" 'IOT2050_FAILLOCK_DENY ?= "5"'; then
    fail "Login security recipe must default deny threshold to 5"
fi
pass "Login security recipe defaults deny threshold to 5"

if ! contains "${login_security_recipe}" 'IOT2050_FAILLOCK_FAIL_INTERVAL ?= "900"'; then
    fail "Login security recipe must default fail_interval to 900"
fi
pass "Login security recipe defaults fail_interval to 900"

if ! contains "${login_security_recipe}" 'IOT2050_FAILLOCK_UNLOCK_TIME ?= "900"'; then
    fail "Login security recipe must default unlock_time to 900"
fi
pass "Login security recipe defaults unlock_time to 900"

if ! contains "${login_security_recipe}" 'IOT2050_FAILLOCK_EVEN_DENY_ROOT ?= "1"'; then
    fail "Login security recipe must default even_deny_root to 1"
fi
pass "Login security recipe defaults even_deny_root to 1"

if ! contains "${login_security_recipe}" 'IOT2050_FAILLOCK_ROOT_UNLOCK_TIME ?= "900"'; then
    fail "Login security recipe must default root_unlock_time to 900"
fi
pass "Login security recipe defaults root_unlock_time to 900"

if ! contains "${login_security_template}" 'deny=${DENY}'; then
    fail "Login security template must render deny into faillock.conf"
fi
pass "Login security template renders deny into faillock.conf"

if ! contains "${login_security_template}" 'dir=${FAILL_DIR}'; then
    fail "Login security template must configure persistent faillock storage"
fi
pass "Login security template configures persistent faillock storage"

if ! contains "${login_security_template}" 'pam_pwquality.so retry=3'; then
    fail "Login security template must add pam_pwquality to common-password"
fi
pass "Login security template adds pam_pwquality to common-password"

if ! contains "${login_security_template}" 'minlen = 12'; then
    fail "Login security template must require 12-character passwords"
fi
pass "Login security template requires 12-character passwords"

if ! contains "${login_security_template}" 'minclass = 3'; then
    fail "Login security template must require three password character classes"
fi
pass "Login security template requires three password character classes"

if ! contains "${login_security_template}" 'fail_interval=${FAIL_INTERVAL}'; then
    fail "Login security template must render fail_interval into faillock.conf"
fi
pass "Login security template renders fail_interval into faillock.conf"

if ! contains "${login_security_template}" 'unlock_time=${UNLOCK_TIME}'; then
    fail "Login security template must render unlock_time into faillock.conf"
fi
pass "Login security template renders unlock_time into faillock.conf"

if ! contains "${login_security_template}" 'echo "even_deny_root"'; then
    fail "Login security template must render even_deny_root when enabled"
fi
pass "Login security template renders even_deny_root when enabled"

if ! contains "${login_security_template}" 'echo "root_unlock_time=${ROOT_UNLOCK_TIME}"'; then
    fail "Login security template must render root_unlock_time when root lockout is enabled"
fi
pass "Login security template renders root_unlock_time when enabled"

if ! contains "${login_security_template}" 'PermitRootLogin no'; then
    fail "Login security template must set PermitRootLogin no for product images"
fi
pass "Login security template sets PermitRootLogin no"

if ! contains "${login_security_template}" 'MaxAuthTries 3'; then
    fail "Login security template must set MaxAuthTries 3"
fi
pass "Login security template sets MaxAuthTries 3"

if ! contains "${login_security_recipe}" 'file://iot2050-failed-login'; then
    fail "Login security recipe must package the failed-login admin helper"
fi
pass "Login security recipe packages the failed-login admin helper"

if ! contains "${login_security_recipe}" 'file://iot2050-account-admin'; then
    fail "Login security recipe must package the local account admin helper"
fi
pass "Login security recipe packages the local account admin helper"

if ! contains "${login_security_recipe}" 'file://iot2050-login-admin'; then
    fail "Login security recipe must package the unified login admin helper"
fi
pass "Login security recipe packages the unified login admin helper"

if ! contains "${login_security_recipe}" 'file://iot2050-login-backend'; then
    fail "Login security recipe must package the privileged login backend helper"
fi
pass "Login security recipe packages the privileged login backend helper"

if ! contains "${login_security_recipe}" 'GROUPS += "iot2050-admin"'; then
    fail "Login security recipe must create iot2050-admin at image build time"
fi
pass "Login security recipe creates iot2050-admin at image build time"

if ! contains "${login_security_recipe}" 'libpam-pwquality'; then
    fail "Login security recipe must install libpam-pwquality"
fi
pass "Login security recipe installs libpam-pwquality"

if ! contains "${login_backend_service}" 'os.getuid()'; then
    fail "Backend service must record the privileged service identity"
fi
pass "Backend service records the privileged service identity"

if ! contains "${login_backend_client}" 'E_BACKEND_UNAVAILABLE'; then
    fail "Login backend client must expose stable unavailable error code"
fi
pass "Login backend client exposes stable unavailable error code"

if ! contains "${login_backend_helper}" 'exec /usr/bin/python3 /usr/lib/iot2050/login-backend-client.py'; then
    fail "Login backend command must dispatch through the socket client"
fi
pass "Login backend command dispatches through the socket client"

if ! contains "${login_security_recipe}" 'file://iot2050-login-backend.service'; then
    fail "Login security recipe must package backend systemd service"
fi
pass "Login security recipe packages backend systemd service"

if ! contains "${login_security_recipe}" 'file://iot2050-login-backend.socket'; then
    fail "Login security recipe must package backend socket unit"
fi
pass "Login security recipe packages backend socket unit"

if ! contains "${login_backend_unit}" 'User=root'; then
    fail "Backend systemd service must run as root"
fi
pass "Backend systemd service runs as root"

if ! contains "${login_backend_socket}" 'SocketGroup=iot2050-admin'; then
    fail "Backend socket must be restricted to iot2050-admin"
fi
pass "Backend socket is restricted to iot2050-admin"

if ! contains "${login_backend_service}" 'SO_PEERCRED'; then
    fail "Backend service must authorize socket peers with SO_PEERCRED"
fi
pass "Backend service authorizes socket peers with SO_PEERCRED"

if [ ! -x "${login_backend_service_test}" ]; then
    fail "Backend service regression test must be executable"
fi
pass "Backend service regression test is executable"

if ! contains "${login_security_recipe}" 'file://login-backend-client.py'; then
    fail "Login security recipe must package backend socket client"
fi
pass "Login security recipe packages backend socket client"

if ! contains "${login_backend_client}" 'getpass.getpass'; then
    fail "Backend client must read passwords without argv"
fi
pass "Backend client reads passwords without argv"

if ! contains "${login_backend_client}" 'SOCKET_PATH = os.environ.get'; then
    fail "Backend client must support controlled socket-path injection"
fi
pass "Backend client supports controlled socket-path injection"

if ! contains "${login_security_recipe}" 'file://login-backend-client.py'; then
    fail "Login security recipe must package backend client implementation"
fi
pass "Login security recipe packages backend client implementation"

if ! contains "${login_security_postinst}" 'groupadd --system iot2050-admin'; then
    fail "Login security postinst must create iot2050-admin"
fi
pass "Login security postinst creates iot2050-admin"

if ! contains "${onboarding_user_script}" "'iot2050-admin'"; then
    fail "Onboarding must grant named administrators iot2050-admin"
fi
pass "Onboarding grants named administrators iot2050-admin"

if ! contains "${onboarding_index}" 'password-guidance'; then
    fail "Onboarding UI must expose password requirements guidance"
fi
pass "Onboarding UI exposes password requirements guidance"

if ! contains "${onboarding_index}" 'data-password-rule="classes"'; then
    fail "Onboarding UI must list password character-class requirements"
fi
pass "Onboarding UI lists password character-class requirements"

if ! contains "${onboarding_web_script}" 'updatePasswordGuidance'; then
    fail "Onboarding UI must update password guidance while typing"
fi
pass "Onboarding UI updates password guidance while typing"

if ! contains "${onboarding_web_script}" 'function handlePasswordInput'; then
    fail "Onboarding UI must show password validation feedback while typing"
fi
pass "Onboarding UI shows password validation feedback while typing"

if ! contains "${onboarding_user_script}" 'PASSWORD_MIN_LENGTH = 12'; then
    fail "Onboarding must enforce the shared password minimum length"
fi
pass "Onboarding enforces the shared password minimum length"

if ! contains "${onboarding_api_script}" 'password.length < 12'; then
    fail "Onboarding API must enforce the password minimum length"
fi
pass "Onboarding API enforces the password minimum length"

if ! contains "${onboarding_web_script}" 'function getPasswordRules'; then
    fail "Onboarding web UI must evaluate the shared password rules"
fi
pass "Onboarding web UI evaluates the shared password rules"

if ! contains "${onboarding_index}" 'At least 12 characters'; then
    fail "Onboarding password field must advertise the password minimum length"
fi
pass "Onboarding password field advertises the password minimum length"

if ! contains "${login_backend_service}" 'PASSWORD_MIN_LENGTH = 12'; then
    fail "Login backend must enforce the shared password minimum length"
fi
pass "Login backend enforces the shared password minimum length"

if ! contains "${account_admin_helper}" 'Usage: $0 [--format text|json] set-password <user> | unlock <user>'; then
    fail "Account admin helper must support set-password and unlock actions with optional format"
fi
pass "Account admin helper supports set-password and unlock actions with optional format"

if ! contains "${account_admin_helper}" 'tool=iot2050-account-admin action='; then
    fail "Account admin helper must emit stable text-mode result fields"
fi
pass "Account admin helper emits stable text-mode result fields"

if ! contains "${account_admin_helper}" 'error_code='; then
    fail "Account admin helper must emit error_code in text-mode output"
fi
pass "Account admin helper emits error_code in text-mode output"

if ! contains "${account_admin_helper}" 'exit_code='; then
    fail "Account admin helper must emit exit_code in text-mode output"
fi
pass "Account admin helper emits exit_code in text-mode output"

if ! contains "${account_admin_helper}" '"tool":"iot2050-account-admin"'; then
    fail "Account admin helper must support stable JSON result output"
fi
pass "Account admin helper supports stable JSON result output"

if ! contains "${account_admin_helper}" '"error_code":"'; then
    fail "Account admin helper JSON output must include error_code"
fi
pass "Account admin helper JSON output includes error_code"

if ! contains "${account_admin_helper}" '"exit_code":'; then
    fail "Account admin helper JSON output must include exit_code"
fi
pass "Account admin helper JSON output includes exit_code"

if ! contains "${account_admin_helper}" 'Refusing to operate on root'; then
    fail "Account admin helper must refuse root operations"
fi
pass "Account admin helper refuses root operations"

if ! contains "${account_admin_helper}" 'Refusing to operate on system account'; then
    fail "Account admin helper must refuse system accounts"
fi
pass "Account admin helper refuses system accounts"

if ! contains "${account_admin_helper}" 'Refusing to operate on non-login service account'; then
    fail "Account admin helper must refuse non-login service accounts"
fi
pass "Account admin helper refuses non-login service accounts"

if ! contains "${account_admin_helper}" 'logger -t "${LOG_TAG}"'; then
    fail "Account admin helper must emit minimal operation logs"
fi
pass "Account admin helper emits minimal operation logs"

if ! contains "${account_admin_helper}" 'passwd "${user_name}"'; then
    fail "Account admin helper must reset passwords through passwd"
fi
pass "Account admin helper resets passwords through passwd"

if ! contains "${account_admin_helper}" 'faillock --user "${user_name}" --reset'; then
    fail "Account admin helper must clear failed-login state after recovery actions"
fi
pass "Account admin helper clears failed-login state after recovery actions"

if ! contains "${failed_login_helper}" 'Usage: $0 [--format text|json] status <user> | reset <user>'; then
    fail "Failed-login helper must support status and reset actions with optional format"
fi
pass "Failed-login helper supports status and reset actions with optional format"

if ! contains "${failed_login_helper}" 'tool=iot2050-failed-login action='; then
    fail "Failed-login helper must emit stable text-mode result fields"
fi
pass "Failed-login helper emits stable text-mode result fields"

if ! contains "${failed_login_helper}" 'error_code='; then
    fail "Failed-login helper must emit error_code in text-mode output"
fi
pass "Failed-login helper emits error_code in text-mode output"

if ! contains "${failed_login_helper}" 'exit_code='; then
    fail "Failed-login helper must emit exit_code in text-mode output"
fi
pass "Failed-login helper emits exit_code in text-mode output"

if ! contains "${failed_login_helper}" '"tool":"iot2050-failed-login"'; then
    fail "Failed-login helper must support stable JSON result output"
fi
pass "Failed-login helper supports stable JSON result output"

if ! contains "${failed_login_helper}" '"error_code":"'; then
    fail "Failed-login helper JSON output must include error_code"
fi
pass "Failed-login helper JSON output includes error_code"

if ! contains "${failed_login_helper}" '"exit_code":'; then
    fail "Failed-login helper JSON output must include exit_code"
fi
pass "Failed-login helper JSON output includes exit_code"

if ! contains "${failed_login_helper}" '"faillock_output":"'; then
    fail "Failed-login helper JSON output must include faillock_output"
fi
pass "Failed-login helper JSON output includes faillock_output"

if ! contains "${failed_login_helper}" 'if [ "${OUTPUT_FORMAT}" = "text" ]; then'; then
    fail "Failed-login helper must keep JSON status output machine-readable"
fi
pass "Failed-login helper keeps JSON status output machine-readable"

if ! contains "${login_admin_helper}" 'Usage: $0 [--format text|json] schema [<domain>/<action>] | schema-id [<domain>/<action>] | failed-login <status|reset> <user> | account <status|set-password|unlock|disable|enable|delete> <user>'; then
    fail "Unified login admin helper must expose schema-id and action-scoped schema interfaces"
fi
pass "Unified login admin helper exposes schema-id and action-scoped schema interfaces"

if ! contains "${login_admin_helper}" 'schema-id)'; then
    fail "Unified login admin helper must implement schema-id command"
fi
pass "Unified login admin helper implements schema-id command"

if ! contains "${login_admin_helper}" 'schema)'; then
    fail "Unified login admin helper must implement schema contract discovery"
fi
pass "Unified login admin helper implements schema contract discovery"

if ! contains "${login_admin_helper}" 'emit_action_schema "$2"'; then
    fail "Unified login admin helper must support single-action schema queries"
fi
pass "Unified login admin helper supports single-action schema queries"

if ! contains "${login_admin_helper}" 'failed-login/status)'; then
    fail "Unified login admin helper must define contract for failed-login/status"
fi
pass "Unified login admin helper defines contract for failed-login/status"

if ! contains "${login_admin_helper}" 'account/unlock'; then
    fail "Unified login admin helper must define contract for account/unlock"
fi
pass "Unified login admin helper defines contract for account/unlock"

if ! contains "${login_admin_helper}" 'account/delete)'; then
    fail "Unified login admin helper must define contract for account/delete"
fi
pass "Unified login admin helper defines contract for account/delete"

if ! contains "${login_admin_helper}" 'output_fields=tool,action,target,result,reason,error_code,exit_code,detail,faillock_output'; then
    fail "Unified login admin helper text schema must advertise faillock_output field"
fi
pass "Unified login admin helper text schema advertises faillock_output field"

if ! contains "${login_admin_helper}" '"schema_version":"1.0.0"'; then
    fail "Unified login admin helper JSON schema must advertise semver schema version"
fi
pass "Unified login admin helper JSON schema advertises semver schema version"

if ! contains "${login_admin_helper}" 'contract_id=iot2050-login-admin/1.0.0/full'; then
    fail "Unified login admin helper text schema must advertise full contract_id"
fi
pass "Unified login admin helper text schema advertises full contract_id"

if ! contains "${login_admin_helper}" '"contract_id":"iot2050-login-admin/1.0.0/full"'; then
    fail "Unified login admin helper JSON schema must advertise full contract_id"
fi
pass "Unified login admin helper JSON schema advertises full contract_id"

if [ ! -f "${login_admin_snapshot_file}" ]; then
    fail "Login-admin schema snapshot file must be present"
fi
pass "Login-admin schema snapshot file is present"

if ! contains "${login_admin_helper}" 'compatibility_versioning=semver'; then
    fail "Unified login admin helper text schema must advertise compatibility versioning"
fi
pass "Unified login admin helper text schema advertises compatibility versioning"

if ! contains "${login_admin_helper}" '"compatibility":{"versioning":"semver"'; then
    fail "Unified login admin helper JSON schema must advertise compatibility policy"
fi
pass "Unified login admin helper JSON schema advertises compatibility policy"

if ! contains "${login_admin_helper}" '"exit_codes":{'; then
    fail "Unified login admin helper JSON schema must advertise exit code mapping"
fi
pass "Unified login admin helper JSON schema advertises exit code mapping"

if ! contains "${login_admin_helper}" 'error_codes=OK,E_PRIVILEGE_REQUIRED,E_PROTECTED_ROOT'; then
    fail "Unified login admin helper schema must advertise privilege error code"
fi
pass "Unified login admin helper schema advertises privilege error code"

if ! contains "${login_admin_helper}" 'exit_codes=OK:0,E_INVALID_USAGE:2,E_PRIVILEGE_REQUIRED:10,E_INVALID_ACTION:2'; then
    fail "Unified login admin helper schema must advertise backend error mappings"
fi
pass "Unified login admin helper schema advertises backend error mappings"

if ! contains "${login_backend_client}" 'Usage: iot2050-login-backend [--format text|json] failed-login'; then
    fail "Login backend client must expose the stable action interface"
fi
pass "Login backend client exposes the stable action interface"

if ! contains "${login_admin_helper}" 'action_contract_failed-login/status=required:'; then
    fail "Unified login admin helper text schema must advertise failed-login status contract"
fi
pass "Unified login admin helper text schema advertises failed-login status contract"

if ! contains "${login_admin_helper}" '"domains":{"failed-login":["status","reset"],"account":["status","set-password","unlock","disable","enable","delete"]}'; then
    fail "Unified login admin helper JSON schema must advertise lifecycle domains"
fi
pass "Unified login admin helper JSON schema advertises lifecycle domains"

if ! contains "${login_admin_helper}" 'exec "$(dirname "$0")/iot2050-login-backend"'; then
    fail "Unified login admin helper must route actions through backend"
fi
pass "Unified login admin helper routes actions through backend"

if ! contains "${failed_login_helper}" 'Refusing to operate on root'; then
    fail "Failed-login helper must refuse root operations"
fi
pass "Failed-login helper refuses root operations"

if ! contains "${failed_login_helper}" 'Refusing to operate on system account'; then
    fail "Failed-login helper must refuse system accounts"
fi
pass "Failed-login helper refuses system accounts"

if ! contains "${failed_login_helper}" 'Refusing to operate on non-login service account'; then
    fail "Failed-login helper must refuse non-login service accounts"
fi
pass "Failed-login helper refuses non-login service accounts"

if ! contains "${failed_login_helper}" 'logger -t "${LOG_TAG}"'; then
    fail "Failed-login helper must emit minimal operation logs"
fi
pass "Failed-login helper emits minimal operation logs"

if ! contains "${failed_login_helper}" 'faillock --user "${user_name}" --reset'; then
    fail "Failed-login helper must reset counters through faillock"
fi
pass "Failed-login helper resets counters through faillock"

if ! contains "${dev_root_ssh_postinst}" 'PermitRootLogin yes'; then
    fail "Dev root SSH compatibility package must restore PermitRootLogin yes"
fi
pass "Dev root SSH compatibility package restores PermitRootLogin yes"

if ! contains "${dev_root_ssh_postinst}" 'rm -f /etc/ssh/sshd_config.d/10-iot2050-product-security.conf'; then
    fail "Dev root SSH compatibility must remove Product root SSH denial"
fi
pass "Dev root SSH compatibility removes Product root SSH denial"

preauth_line="$(line_number "${login_security_template}" 'pre = "auth required pam_faillock.so preauth"')"
authfail_line="$(line_number "${login_security_template}" 'fail = "auth [default=die] pam_faillock.so authfail"')"
authsucc_line="$(line_number "${login_security_template}" 'succ = "auth sufficient pam_faillock.so authsucc"')"

if [ -z "${preauth_line}" ] || [ -z "${authfail_line}" ] || [ -z "${authsucc_line}" ]; then
    fail "Login security template must define preauth/authfail/authsucc PAM snippets"
fi

if [ "${preauth_line}" -ge "${authfail_line}" ] || [ "${authfail_line}" -ge "${authsucc_line}" ]; then
    fail "Login security template must keep preauth, authfail and authsucc snippet definitions in stable order"
fi
pass "Login security template keeps stable PAM snippet definition order"

if ! bash "${login_admin_dynamic_checker}"; then
    fail "Dynamic login-admin schema contract checks must pass"
fi
pass "Dynamic login-admin schema contract checks pass"

if ! bash "${login_admin_snapshot_checker}"; then
    fail "Login-admin schema snapshot checks must pass"
fi
pass "Login-admin schema snapshot checks pass"

if [ -x "${login_runtime_remote_checker}" ]; then
    pass "Remote runtime checker available at ${login_runtime_remote_checker}"
fi

if ! contains "${login_runtime_remote_checker}" '--lifecycle-user USER'; then
    fail "Remote runtime checker must expose the read-only lifecycle probe option"
fi
pass "Remote runtime checker exposes the read-only lifecycle probe option"

if ! contains "${login_runtime_remote_checker}" 'account status "${LIFECYCLE_USER}"'; then
    fail "Remote lifecycle probe must use account status only"
fi
pass "Remote lifecycle probe uses account status only"

if ! contains "${login_runtime_remote_checker}" '--lifecycle-test-user USER'; then
    fail "Remote runtime checker must expose the guarded lifecycle integration test"
fi
pass "Remote runtime checker exposes the guarded lifecycle integration test"

if ! contains "${login_runtime_remote_checker}" 'iot2050-rt-'; then
    fail "Lifecycle integration test must restrict temporary account names"
fi
pass "Lifecycle integration test restricts temporary account names"

if ! contains "${login_runtime_remote_checker}" 'userdel --remove'; then
    fail "Lifecycle integration test must clean up its temporary account"
fi
pass "Lifecycle integration test cleans up its temporary account"

echo "[PASS] Account policy composition checks completed"
