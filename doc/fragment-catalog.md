# Fragment Catalog (Descriptors & Optional Fragments)

_Applies to version: v1.6.0+_

This catalog lists supplemental KAS fragments and descriptors beyond the
primary feature set, which is summarized in the top-level `README.md` and in
the "Image Glossary" of `build-config.md`.

Use this as a reference when composing specialized build chains for tasks like:
- Real-time kernels
- Deterministic CI builds
- Upstream kernel validation
- Secure storage provisioning
- Mirror control

## Legend
- **Descriptor**: A full base or standalone build target that produces a
  distinct set of artifacts.
- **Fragment**: Adds or modifies configuration when chained after a descriptor.

## Table: Infrastructure / Advanced Fragments
| Name | Purpose | Typical Use Case |
|------|---------|------------------|
| `preempt-rt.yml` | Switch kernel to PREEMPT_RT (`KERNEL_NAME=iot2050-rt`) | Low-latency / control / industrial jitter tests |
| `package-lock.yml` | Reproducible APT snapshot pin (`ISAR_USE_APT_SNAPSHOT=1`) | Deterministic CI & release traceability |
| `rpmb-setup.yml` | Add OP-TEE / UEFI STMM RPMB setup overrides | Preparing secure storage / RPMB provisioning |
| `debian-mirror.yml` | Override Debian mirror & premirror mapping | Local mirror, bandwidth or regional acceleration |
| `upstream.yml` | Track upstream kernel version (e.g. 6.x line) | Early HW enablement, regression testing |

## Secure Boot & Provisioning
The `secure-boot.yml` fragment enables the core secure boot feature set. It can
be combined with provisioning fragments to prepare the device for secure
operation.

- `rpmb-setup.yml`: Used solely for RPMB (Replay Protected Memory Block)
  provisioning. This prepares the secure storage partition.
- `kas/opt/otpcmd/*.yml`: A collection of fragments for specific provisioning
  tasks, like writing keys to one-time programmable fuses.

These are typically combined with firmware-only descriptors like
`kas-iot2050-boot.yml`.

Prepare the RPMB partition (no secure boot signing):
```sh
./kas-container build kas-iot2050-boot.yml:kas/opt/rpmb-setup.yml
```
Enable secure boot and provision keys:
```sh
./kas-container build kas-iot2050-boot.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml
```

## Example Composite Chains
Real-time + reproducible + demos:
```sh
./kas-container build kas-iot2050-example.yml:kas/opt/preempt-rt.yml:kas/opt/package-lock.yml
```