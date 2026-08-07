# Host Validation Scripts

These scripts validate the IOT2050 login-security recipe from the repository
checkout. Run them from the repository root and use `bash` for shell scripts.

## Validation levels

### Static policy composition

```sh
bash scripts/host/check-account-policy.sh
```

Checks Example/Dev KAS composition, PAM and SSH policy sources, package
contents, backend authorization boundaries, onboarding behavior, and the
available validation tools. It also runs the dynamic contract and schema
snapshot checks.

### Login-admin contract matrix

```sh
bash scripts/host/check-login-admin-contract.sh
```

Validates text/JSON schema discovery, schema IDs, supported actions, stable
error contracts, backend-unavailable behavior, and local backend protocol
coverage.

### Schema snapshots

```sh
bash scripts/host/check-login-admin-schema-snapshot.sh
```

Compares hashes of selected `iot2050-login-admin` schema outputs with
`scripts/host/login-admin-schema-snapshots.txt`. The snapshot file is a
compatibility regression baseline: update it only when a schema change is
intentional and review the corresponding contract change in the same change
set.

### Backend service regression test

```sh
bash scripts/host/test-login-backend-service.sh
```

Uses mocked accounts and does not modify the host. It covers authorization,
root and system-account protection, last-admin protection, lifecycle command
selection, and weak-password rejection.

### Backend client protocol test

```sh
bash scripts/host/test-login-backend-client.sh
```

Starts a temporary Unix socket server and verifies the JSON request/response
protocol used by the backend client. The temporary server and socket are
removed automatically.

## Target-device runtime validation

The remote checker requires an SSH connection and sudo privileges. Without a
password option it prompts interactively:

```sh
bash scripts/host/check-login-runtime-remote.sh
```

It checks the admin group, backend socket/service, SSH policy, faillock
persistence, CrackLib dictionary presence, and a backend smoke response.

A read-only account status probe can be added for an existing account:

```sh
bash scripts/host/check-login-runtime-remote.sh \
    --lifecycle-user <existing-user>
```

The full lifecycle integration test is destructive and must only run on a
test device. The account name is restricted to the `iot2050-rt-` prefix:

```sh
bash scripts/host/check-login-runtime-remote.sh \
    --lifecycle-test-user iot2050-rt-a
```

This mode creates a temporary account, tests disable/enable/status/delete,
and removes the account on failure. Do not use a production administrator.

## Recommended order

For source-only validation:

```sh
bash scripts/host/test-login-backend-client.sh
bash scripts/host/test-login-backend-service.sh
bash scripts/host/check-login-admin-contract.sh
bash scripts/host/check-login-admin-schema-snapshot.sh
bash scripts/host/check-account-policy.sh
```

For a rebuilt target image:

```sh
bash scripts/host/check-login-runtime-remote.sh
bash scripts/host/check-login-runtime-remote.sh \
    --lifecycle-user <existing-user>
```

Run the destructive lifecycle test only after the read-only checks pass.
