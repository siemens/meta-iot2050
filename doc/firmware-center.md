# Firmware Center

The Firmware Center integrates system, EIO controller, and EIO module firmware
operations into one Cockpit page. It deliberately keeps the three update
domains separate: they share transport, task persistence, and presentation,
but not package formats or flashing logic.

## Components

| Component | Location | Responsibility |
| --- | --- | --- |
| Cockpit package | `/usr/share/cockpit/iot2050-firmware` | File selection, inspection results, confirmation, and task status |
| Local client | `/usr/sbin/iot2050-fwmgr` | JSON command adapter used by Cockpit with `superuser: require` |
| Manager | `/usr/lib/iot2050/firmware-manager` | Provider discovery, staging, task persistence, and hardware-operation locking |
| Manager socket | `/run/iot2050/firmware-manager.sock` | Root-only, systemd-activated JSON Lines IPC |
| SM providers | `iot2050-firmware-provider-sm` | Controller and module adapters installed only with SM support |

No HTTP firmware API or additional listening network port is introduced.
Cockpit invokes the local client through its existing privilege boundary.

## Runtime model

The protocol version is `1`. Each request and response occupies one JSON line.
The currently supported operations are:

- `capabilities.list`: list providers that are available on this device.
- `staging.import`: copy a local file into private manager storage and return a
  token, size, name, and SHA-256 digest.
- `inspect.get`: perform provider-specific checks without writing hardware.
- `action.start`: start one persistent hardware task.
- `task.get`: retrieve the durable task state.

Only one hardware operation can run at a time. Tasks transition through
`queued`, `running`, and `succeeded` or `failed`. A task left in `queued` or
`running` after manager restart is marked `failed/interrupted`; automatic flash
resume is intentionally not attempted.

Provider descriptors in `providers.d` isolate optional hardware support. A bad
optional descriptor is logged and skipped instead of disabling the System
Firmware provider.

## Security boundaries

### Staging

The manager copies input through an `O_NOFOLLOW` file descriptor, accepts only
regular files, enforces a size limit, and stores data and metadata under a
root-only directory. `resolve()` recomputes size and SHA-256 before every
inspection or update so that a modified staged object is rejected.

Tokens are capabilities for files already inside manager-controlled storage;
providers never accept arbitrary paths from Cockpit.

### System Firmware

Managed System Firmware updates have stricter behavior than the legacy CLI:

- A signature is mandatory and is verified during inspection and again before
  flashing.
- The package is extracted into a private temporary directory.
- Only flat regular-file tar members are accepted. Absolute paths, parent
  traversal, directories, symbolic links, hard links, and device nodes are
  rejected.
- Member count and total extracted size are bounded.
- A backup is always created under `/var/lib/iot2050-fwmgr/system-backup`.
- The managed path never prompts, retries a failed flash, or reboots.

The CLI remains backward compatible: `--verify` is still optional there, and
its existing arguments and numeric return codes remain stable. New code must
not implement the Web path by calling the CLI `main()` because that would
inherit interactive confirmation and blind retry behavior.

### SM-only providers

SM provider packaging is controlled by `IOT2050_SM_SUPPORT`. At runtime, the
device-tree compatible string is the hardware identity boundary and EIOFS
nodes prove service readiness. Hiding a card in the browser is not treated as
authorization; provider availability is checked again in the manager.

`firmware_a` and `firmware_b` refer to chip A and chip B inside a module. They
are not redundant banks. Module slots are validated as `1..6` by the backend.

## Provider contracts

### System

Source: staged signed tar package. Inspection returns the selected firmware
name, target version and board, firmware SHA-256, and signature status. Update
always backs up and reports that a reboot is required.

### EIO controller

Source: image-default firmware only. Inspection reports runtime and bundled
versions, metadata SHA-1, actual SHA-256, update need, and integrity. The
current controller format is not signature-verified; the UI must display the
hash before confirmation and the provider performs readback after flashing.

### Module

Source: independently staged chip A and/or chip B images. Updates preserve the
existing CLI order (A then B) and report per-chip outcomes. A successful A
write followed by a failed B write remains a partial update and must not be
reported as an atomic rollback.

## Maintenance

When adding a provider:

1. Keep domain-specific validation and flashing in its existing package.
2. Implement `available()`, `capabilities()`, and `inspect()`; add `start()` only
   when writing is supported.
3. Consume staging tokens rather than caller paths.
4. Return stable `ManagerError` codes and avoid exposing tracebacks or private
   paths through IPC.
5. Add host-side contract tests and verify the resulting Debian package.

The host-side test suite is under `tests/firmware_center`. Recipe metadata and
package builds should be run through `kas-container` so `/repo` and Isar paths
match the supported build environment.

Hardware writes require separate on-device validation. In particular, test
power-loss handling, backup readability, flash readback, EIOFS readiness, and
post-update reboot behavior on representative Basic, Advanced, and SM boards.
