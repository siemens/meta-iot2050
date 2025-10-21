# Fragment Catalog (Descriptors & Optional Fragments)

_Applies to version: v1.6.0+_

This catalog lists supplemental KAS fragments and descriptors beyond the
primary feature set already summarized in the top-level `README.md` and in
the "Image Glossary" of `build-config.md`.

Use this as a reference when composing specialized build chains
(real-time kernels, deterministic CI builds, upstream kernel validation,
secure storage provisioning, mirror control, etc.).

## Legend
- Descriptor: full base or standalone build target (produces distinct artifact set)
- Fragment: adds or modifies configuration when chained after a descriptor

## Table: Infrastructure / Advanced Fragments
| Name | Type | Purpose | Typical Use Case | Caveats / Notes |
|------|------|---------|------------------|-----------------|
| `preempt-rt.yml` | Fragment | Switch kernel to PREEMPT_RT (`KERNEL_NAME=iot2050-rt`) | Low-latency / control / industrial jitter tests | Slightly higher maintenance; validate with your workload |
| `package-lock.yml` | Fragment | Reproducible APT snapshot pin (`ISAR_USE_APT_SNAPSHOT=1`) | Deterministic CI & release traceability | Must refresh timestamp periodically; can delay security fixes |
| `rpmb-setup.yml` | Fragment | Add OP-TEE / UEFI STMM RPMB setup overrides | Preparing secure storage / RPMB provisioning | Usually combined with secure-boot & provisioning fragments |
| `debian-mirror.yml` | Fragment | Override Debian mirror & premirror mapping | Local mirror, bandwidth or regional acceleration | Ensure mirror sync/freshness; fallback to default if stale |
| `upstream.yml` | Fragment | Track upstream kernel version (e.g. 6.x line) | Early HW enablement, regression testing | Less stable; pair with `package-lock.yml` for reproducibility |

## Secure Boot & Provisioning Relationship
Provisioning fragments in `kas/opt/otpcmd/` (referenced in
`build-config.md`) can be combined with: `secure-boot.yml`,
`rpmb-setup.yml`, and the boot / firmware update descriptors. Order these
after the base descriptor but before tooling fragments like `sdk.yml`.

Recommended ordering snippet:
```bash
./kas-container build \
  kas-iot2050-boot.yml:kas/opt/secure-boot.yml:kas/opt/rpmb-setup.yml:kas/opt/otpcmd/key-provision.yml
```

## Example Composite Chains
Real-time + reproducible + demos:
```bash
./kas-container build kas/iot2050.yml:kas/opt/preempt-rt.yml:kas/opt/package-lock.yml:kas/opt/example.yml
```
Upstream kernel evaluation with lock & Hailo:
```bash
./kas-container build kas-iot2050-example.yml:kas/opt/upstream.yml:kas/opt/package-lock.yml:kas/opt/hailo.yml
```
Firmware provisioning (no rootfs):
```bash
./kas-container build kas-iot2050-boot.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml
```

## Interaction Notes
| Combination | Status | Rationale |
|-------------|--------|-----------|
| preempt-rt + secure-boot | Supported | Kernel name change does not affect signing flow |
| upstream + package-lock | Recommended | Stabilizes dependency versions for reproducibility |
| upstream only (no lock) | Allowed (volatile) | Useful for quick regression triage |
| package-lock + debian-mirror | Supported (mirror ignored if snapshot present) | Snapshot takes precedence; mirror changes affect only non-pinned pulls |
| rpmb-setup without secure-boot | Supported (prep) | Allows staging RPMB content ahead of securing boot |

## Legacy & Migration Cross-Reference
Historic fragment names removed in the refactor (see Legacy Fragment Mapping
in `build-config.md`):
- `eio.yml` → replaced by `sm.yml`
- `module.yml` → compose with `sm.yml` + other feature fragments
- `no-node-red.yml` → simply omit `node-red.yml`

## Reproducibility Tips
- Pair `package-lock.yml` with a dated commit reference in release notes.
- Mirror overrides (`debian-mirror.yml`) are ignored when snapshot locking is
  active (expected).
- For long-lived branches, periodically rebase the snapshot date after
  security review.

## Where to Document Future Fragments
Add new infrastructure or provisioning fragments here and (if user-facing)
consider a brief mention in the main README matrix if they affect runtime
capabilities. Otherwise keep them in this catalog + `build-config.md`
ordering rules.

## See Also
- `build-config.md` (section 3 & appendix for ordering)
- `secure-boot.md`
- `maintenance.md`
- Top-level README matrix
