# Firmware Center implementation notes

This document records the implementation boundaries needed by developers and
maintainers. User-facing operation guidance is provided locally by the `?`
help in the Firmware Center and by the confirmation messages shown before
hardware writes.

## Runtime boundary

The browser calls `/usr/sbin/iot2050-fwmgr` through Cockpit's
`superuser: require` privilege flow. The browser does not access firmware
files, hardware devices, gRPC sockets, or public firmware HTTP APIs.

A write creates a durable task under the fwmgr state directory and starts one
systemd template worker. The worker invokes the selected provider. A task can
be inspected after a browser reconnect; a worker that disappears while a task
is running is recorded as interrupted rather than resumed automatically.

The provider transport matrix is:

| Domain | Provider transport | Hardware backend |
| --- | --- | --- |
| Firmware | Root-only Firmware gRPC | OSPI, U-Boot, MTD |
| EIO Controller | Existing EIOManager gRPC | flashrom and EIO controller |
| EIO Module | Root-only Module Firmware gRPC | Existing EIOFS module backend |

The `iot2050-module-firmware-update` command is a CLI client for the Module
Firmware gRPC service, mirroring the pre-gRPC CLI behavior. The gRPC service
itself is started by `iot2050-module-firmware.service` from the
`iot2050-module-firmware-service` executable.

## Operation contracts

Firmware services execute long-running writes asynchronously. `Update` and,
for the firmware service, `Rollback` return only after the service accepts the
single local operation; the gRPC request is not held open for the duration of
the flash. `GetStatus` returns the durable state of the current or latest
operation. `WatchLogs` provides best-effort, human-readable messages while a
write is running; messages are not persisted, replayed, or resumed after a
disconnect or service restart.

Each domain service admits one local hardware write at a time and keeps only
its current/latest state in memory. A service restart clears that state and
never resumes hardware work. The fwmgr task remains the user-facing durable
history and records an interrupted worker, while globally serializing managed
writes across firmware providers.

Firmware uses the service process `HOME` as its backup identity. Managed
requests use this service-owned backup and always verify the package
signature. Explicit backup-directory and signature options are restricted to
the command-line firmware client and require the configured security checks.

EIO Controller keeps the legacy `CheckFWU` status and JSON message for old
clients. New clients may consume the typed `inspection` field. Module results
include slot, Chip A, Chip B, and partial-completion information.

## Resource ownership

Firmware and Module Firmware operations use a single worker for hardware
writes. Each service atomically admits one running operation, while its gRPC
request executor can concurrently serve log streams and status queries. The
fwmgr task layer separately serializes operations across providers.

## Staging and privilege invariants

Uploaded files are copied into private fwmgr staging storage through a
no-follow file descriptor. Only regular files within the configured size limit
are accepted. A staging token is resolved by recomputing its size and
SHA-256 digest before use.

Providers receive staging tokens or service-controlled data, never arbitrary
browser paths. Root-only Unix sockets and Cockpit privilege escalation are
separate authorization boundaries; hiding a card in the UI is not
authorization.

## Extension rules

New providers should keep validation and flashing in the domain package and
implement the fwmgr provider contract: `available()`, `capabilities()`,
`inspect()`, and, when applicable, `start()`.

Keep user instructions, warnings, and recovery guidance in the page help and
confirmation UI. Keep this file limited to stable implementation contracts
that are useful when changing packages or backends.
