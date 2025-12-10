# Build Configuration Guide (Menu & Manual)

> TL;DR: Use `./kas-container menu` for discovery; copy the printed colon
> chain into CI. One base descriptor + zero or more feature / security /
> tooling fragments.

## Concepts
Two equivalent workflows exist:
1. Interactive ncurses (Kconfig) menu
2. Manual fragment chaining (deterministic, CI-friendly)

**Terminology**:
- **Descriptor (base)**: Top-level KAS file defining an image or boot/update
  artifact (e.g., `kas-iot2050-example.yml`). Exactly one per build chain.
- **Fragment**: Optional KAS file layered after the base to add features,
  security provisioning, tooling, or environment control (e.g.,
  `kas/opt/node-red.yml`).
- **Chain**: The full colon-separated sequence supplied to `kas-container build`.

## Interactive Menu Workflow
### Launch
```sh
./kas-container menu
```
The wrapper parses `Kconfig`, shows choices, saves the selection, and prints
the corresponding build command.

### Image Types (Choices & Glossary)
Select exactly one primary build target (descriptor). Naming is stable even
if prompt wording evolves.

| Menu Label | Descriptor / Invocation | Intent Summary | Notes |
|------------|-------------------------|----------------|-------|
| Example image | `kas-iot2050-example.yml` | Full showcase: demos + Node-RED + SM included | Fastest path to feature parity |
| Example image (SWUpdate A/B) | `kas-iot2050-swupdate.yml` | Example image + dual-copy SWUpdate layout (.swu) | Produces `.wic` + `.swu` |
| Example image (minimal HW enablement) | `kas/iot2050.yml` | Bare BSP; add fragments to reach showcase | Use for custom lean variants |
| Firmware boot images | `kas-iot2050-boot.yml` | Boot firmware artifacts only | No rootfs image produced |
| Firmware update package | `kas-iot2050-fwu-package.yml` | Boot chain update bundle (no rootfs) | Field firmware update payload |
| QEMU image (emulated target) | `:<kas-iot2050-qemu.yml>` (chained) | Emulation add-on | Append to minimal or example |

### Feature Toggles (Maps → Fragments)
| Toggle (Menu) | Fragment | Purpose | Visibility |
|---------------|----------|---------|------------|
| Node-RED support | `kas/opt/node-red.yml` | Adds meta-node-red packages | Minimal variant toggle; implicit in Example/SWUpdate |
| SM variant support | `kas/opt/sm.yml` | SM hardware variant (sensors/EIO) | Minimal variant toggle; implicit in Example/SWUpdate |
| Example demo content | `kas/opt/example.yml` | Demo apps and configs from example image | Minimal variant toggle; implicit in Example/SWUpdate |
| Docker support | `kas/opt/docker.yml` | Docker engine/tooling | All images |
| LXDE graphical UI | `kas/opt/lxde.yml` | Lightweight desktop | All images |
| Meta-Hailo AI card support | `kas/opt/hailo.yml` | Hailo driver & runtime | All (board HW required) |
| Preempt-RT kernel | `kas/opt/preempt-rt.yml` | RT tuned kernel | All images |
| Build SDK | `kas/opt/sdk.yml` | Cross SDK outputs | All images (produces SDK tarball) |
| Secure boot & Data encryption | `kas/opt/secure-boot.yml` | Signing, verity, encrypted data | SWUpdate/Firmware contexts |
| OTP Provisioning | `kas/opt/otpcmd/*.yml` | Embed OTP command payload | With secure boot & firmware images |
| OPTEE RPMB setup | `kas/opt/rpmb-setup.yml` | One-time RPMB pairing build | Firmware / secure boot contexts |
| Use packages from release | `kas/opt/package-lock.yml` | Reproducible Debian pkg set | All images |
| Use specific Debian mirror | `kas/opt/debian-mirror.yml` | Override mirror host | All images |

**Notes**:
- Minimal-only toggles appear because Example & SWUpdate already bundle
  those fragments.
- Some provisioning fragments are intentionally hidden unless a compatible
  base descriptor (firmware / secure boot context) is selected.

Visibility of options follows `depends on` in `Kconfig`.

## Manual Composition
The syntax follows this pattern:
```sh
./kas-container build <descriptor>.yml[:<fragment>.yml[:<fragment>.yml ...]]
```
**Ordering guidance** (left→right):
1. Base descriptor (example / swupdate / minimal / boot / fwu)
2. Feature fragments (example, node-red, sm, hailo, docker, lxde, preempt-rt)
3. Security & provisioning (secure-boot, otpcmd/*, rpmb-setup)
4. Tooling & reproducibility (sdk, package-lock, debian-mirror, qemu)

### Build Cheat Sheet
| Purpose | Chain | Outputs | Notes |
|---------|-------|---------|-------|
| Full example | `kas-iot2050-example.yml` | .wic | demos + Node-RED + SM bundled |
| SWUpdate A/B | `kas-iot2050-swupdate.yml` | .wic + .swu | dual rootfs update |
| Minimal BSP | `kas/iot2050.yml` | .wic | lean base |
| Minimal parity (example) | `kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml` | .wic | matches example image |
| Example + Hailo | `kas-iot2050-example.yml:kas/opt/hailo.yml` | .wic | Hailo runtime |
| Example + LXDE + Docker | `kas-iot2050-example.yml:kas/opt/lxde.yml:kas/opt/docker.yml` | .wic | GUI + containers |
| Secure boot (sign only) | `kas-iot2050-swupdate.yml:kas/opt/secure-boot.yml` | signed .wic | replace demo keys |
| Firmware boot chain | `kas-iot2050-boot.yml` | boot binaries | no rootfs |
| Secure boot + provisioning | `kas-iot2050-boot.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml` | enforcing firmware | irreversible OTP actions |
| Firmware update package | `kas-iot2050-fwu-package.yml` | .tar.xz | boot chain update bundle |
| SDK | `kas-iot2050-example.yml:kas/opt/sdk.yml` | SDK tarball | cross toolchain |
| QEMU parity build | `kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml:kas-iot2050-qemu.yml` | virt .wic | emulated target |

### Descriptor Roles
- `kas-iot2050-example.yml`: Full showcase (fastest path).
- `kas-iot2050-swupdate.yml`: A/B layout + .swu artifact.
- `kas/iot2050.yml`: Minimal base; compose features explicitly.
- `kas-iot2050-boot.yml`: Boot firmware only (for signing/provisioning flows).
- `kas-iot2050-fwu-package.yml`: Field firmware update bundle.
- `kas-iot2050-qemu.yml`: Emulation add-on (always chained).

### Security, Provisioning & Reproducibility
**Demo Keys Warning**: `secure-boot.yml` ships with **DEMONSTRATION** keys.
These **MUST** be replaced before any production use.

Provisioning fragments (`otpcmd/*`) trigger irreversible OTP hardware fuse
burns. Include exactly one and only when intentionally programming the device.

**Reproducibility tips**:
- Add `package-lock.yml` to freeze the Debian package set.
- Optionally pin the mirror with `debian-mirror.yml`.
- Use a clean workspace for audit / release builds.
- Consider pairing the RT kernel (`preempt-rt.yml`) with package locking for
  a deterministic kernel and userspace.

### QEMU & Emulation
Basic run (full example):
```sh
./kas-container build kas-iot2050-example.yml:kas-iot2050-qemu.yml
```
Launch with the helper script: `./scripts/host/start-qemu-iot2050.sh` (see
[qemu](qemu.md) for details).

## Legacy Fragment Mapping (Reference)
Historic fragments (now removed) and their modern equivalents:

| Removed Fragment | Replacement / Action |
|------------------|----------------------|
| `eio.yml` | Use `sm.yml` (SM/EIO now unified) |
| `module.yml` | Combine `sm.yml` + other feature fragments as needed |
| `no-node-red.yml` | Simply omit `node-red.yml` when using the minimal base |

Rationale & migration details: see
[layer-architecture](layer-architecture.md).

## Related
- [layer-architecture](layer-architecture.md)
- [maintenance](maintenance.md)
- [swupdate](swupdate.md)
- [sdk](sdk.md)
- [fragment-catalog](fragment-catalog.md)
