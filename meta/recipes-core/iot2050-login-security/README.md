# IOT2050 Login Security

This recipe provides the login-security baseline and local account-management
backend for IOT2050 images.

## What it provides

- Persistent failed-login tracking through PAM `faillock`.
- Password-quality checks through PAM `pwquality` and CrackLib.
- Named-account password reset and failed-login recovery helpers.
- A root-owned, systemd-activated Unix socket backend.
- Stable text and JSON result contracts for operators and automation.
- Account lifecycle operations with protection for the last usable administrator.

## Runtime architecture

```text
iot2050-login-admin
        |
iot2050-login-backend client
        |
/run/iot2050/login-backend.sock
        |
systemd socket activation
        |
login-backend-service.py
        |
passwd / chpasswd / faillock / usermod / userdel
```

The socket is owned by `root`, uses group `iot2050-admin`, and has mode `0660`.
The service also checks the peer credentials with `SO_PEERCRED` before running
an account operation.

## Command-line tools

Inspect or clear failed-login state:

```sh
sudo iot2050-failed-login status <user>
sudo iot2050-failed-login reset <user>
```

Change a named user's password and clear its failed-login state:

```sh
sudo iot2050-account-admin set-password <user>
```

Clear only the PAM failed-login counters. This does not change the password or
re-enable an account disabled by a lifecycle operation:

```sh
sudo iot2050-account-admin unlock <user>
```

The unified entry point exposes schema discovery and routes account actions
through the privileged backend:

```sh
sudo iot2050-login-admin schema
sudo iot2050-login-admin schema-id
sudo iot2050-login-admin account status <user>
sudo iot2050-login-admin account disable <user>
sudo iot2050-login-admin account enable <user>
sudo iot2050-login-admin account delete <user>
```

Use `--format json` for automation. Text output is intended for interactive
operation and shell logs; JSON output provides stable machine-readable fields
and exit codes.

## Account safety rules

The helpers and backend reject:

- The `root` account.
- System accounts.
- Non-login service accounts.
- Invalid or unknown account names.
- Disabling or deleting the last usable `iot2050-admin` administrator.

State-changing operations are executed by the root-owned backend after peer
authorization. Passwords are not placed in command arguments or audit logs.

## Password policy

The image configures a shared password policy for interactive and automated
password changes:

- At least 12 characters.
- At least 3 of 4 character classes: lowercase, uppercase, digits, and symbols.
- No four repeated characters in a row.
- No simple numeric sequences such as `1234`.
- CrackLib dictionary checks are enabled with an explicit runtime wordlist.

The onboarding UI shows these requirements while the user types. The backend
and PAM enforce the policy again, so the browser is only a usability aid and
not a security boundary.

## Configuration files

The package maintainer script is generated from `files/postinst.tmpl` by ISAR.
It configures:

- `/etc/security/faillock.conf`
- `/etc/security/pwquality.conf`
- `/etc/pam.d/common-auth`
- `/etc/pam.d/common-account`
- `/etc/pam.d/common-password`
- `/etc/ssh/sshd_config.d/10-iot2050-product-security.conf`

Failed-login state is stored under `/var/lib/faillock` so it can survive a
service restart and reboot.

## Local validation

Run the repository checks from the workspace root:

```sh
bash scripts/host/test-login-backend-client.sh
bash scripts/host/test-login-backend-service.sh
bash scripts/host/check-login-admin-contract.sh
bash scripts/host/check-login-admin-schema-snapshot.sh
bash scripts/host/check-account-policy.sh
```

The target-device checker validates the installed socket, service, PAM state,
CrackLib dictionary, and backend contract:

```sh
bash scripts/host/check-login-runtime-remote.sh
```

A destructive lifecycle integration test is opt-in and restricted to temporary
account names beginning with `iot2050-rt-`:

```sh
bash scripts/host/check-login-runtime-remote.sh \
    --lifecycle-test-user iot2050-rt-a
```
