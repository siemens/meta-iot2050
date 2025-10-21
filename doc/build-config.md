# Build Configuration Guide (Menu & Manual)
_Applies to version: v1.6.0+_

> TL;DR: Use `./kas-container menu` for discovery; copy the printed colon
> chain into CI. One base descriptor + zero or more feature / security /
> tooling fragments.

## 1. Concepts
Two equivalent workflows exist:
1. Interactive ncurses (Kconfig) menu
2. Manual fragment chaining (deterministic, CI-friendly)

Terminology:
- Descriptor (base): Top-level KAS file defining an image or boot/update
  artifact (e.g. `kas-iot2050-example.yml`). Exactly one per build chain.
- Fragment: Optional KAS file layered after the base to add features,
  security provisioning, tooling, or environment control (e.g.
  `kas/opt/node-red.yml`).
- Chain: The full colon-separated sequence supplied to `kas-container build`.

Evaluation is strictly left→right; later fragments may append packages or
override variables from earlier ones.

## 2. Interactive Menu Workflow
### 2.1 Launch
```
./kas-container menu
```
The wrapper parses `Kconfig`, shows choices, saves selection, prints the
build command.

<a id="2-image-type-choices"></a>
### 2.2 Image Types (Choices & Glossary)
Select exactly one primary build target (descriptor). Naming is stable even
if prompt wording evolves.

| Menu Label | Descriptor / Invocation | Intent Summary | Notes |
|------------|-------------------------|----------------|-------|
| Example image (recommended) | `kas-iot2050-example.yml` | Full showcase: demos + Node-RED + SM included | Fastest path to feature parity |
| Example image (SWUpdate A/B) | `kas-iot2050-swupdate.yml` | Example image + dual-copy SWUpdate layout (.swu) | Produces `.wic` + `.swu` |
| Example image (minimal HW enablement) | `kas/iot2050.yml` | Bare BSP; add fragments to reach showcase | Use for custom lean variants |
| Firmware boot images | `kas-iot2050-boot.yml` | Boot firmware artifacts only | No rootfs image produced |
| Firmware update package | `kas-iot2050-fwu-package.yml` | Boot chain update bundle (no rootfs) | Field firmware update payload |
| QEMU image (emulated target) | `:<kas-iot2050-qemu.yml>` (chained) | Emulation add-on | Append to minimal or example |

### 2.3 Feature Toggles (Maps → Fragments)
| Toggle (Menu) | Fragment | Purpose | Visibility |
|---------------|----------|---------|------------|
| Node-RED support | kas/opt/node-red.yml | Adds meta-node-red packages | Minimal variant toggle; implicit in Example/SWUpdate |
| SM variant support | kas/opt/sm.yml | SM hardware variant (sensors/EIO) | Minimal variant toggle; implicit in Example/SWUpdate |
| Example demo content | kas/opt/example.yml | Demo apps and configs from example image | Minimal variant toggle; implicit in Example/SWUpdate |
| Docker support | kas/opt/docker.yml | Docker engine/tooling | All images |
| LXDE graphical UI | kas/opt/lxde.yml | Lightweight desktop | All images |
| Meta-Hailo AI card support | kas/opt/hailo.yml | Hailo driver & runtime | All (board HW required) |
| Preempt-RT kernel | kas/opt/preempt-rt.yml | RT tuned kernel | All images |
| Build SDK | kas/opt/sdk.yml | Cross SDK outputs | All images (produces SDK tarball) |
| Secure boot & Data encryption | kas/opt/secure-boot.yml | Signing, verity, encrypted data | Example/SWUpdate/Firmware contexts |
| OTP Provisioning | kas/opt/otpcmd/*.yml | Embed OTP command payload | With secure boot & firmware images |
| OPTEE RPMB setup | kas/opt/rpmb-setup.yml | One-time RPMB pairing build | Firmware / secure boot contexts |
| Use packages from release | kas/opt/package-lock.yml | Reproducible Debian pkg set | All images |
| Use specific Debian mirror | kas/opt/debian-mirror.yml | Override mirror host | All images |

Notes:
- Minimal-only toggles appear because Example & SWUpdate already bundle
  those fragments.
- Some provisioning fragments are intentionally hidden unless a compatible
  base descriptor (firmware / secure boot context) is selected.

Visibility of options follows `depends on` in `Kconfig`.

### 2.4 Secure Boot / OTP Sub-Choice
Provisioning variants are mutually exclusive (`choice` block). Pick exactly
one when provisioning.

### 2.5 Saving & Exiting
- Space/Enter toggles bools
- Enter opens a choice list
- S or on-exit prompt saves
- Printed command = canonical manual equivalent

## 3. Manual Composition
Syntax pattern:
```
./kas-container build <descriptor>.yml[:<fragment>.yml[:<fragment>.yml ...]]
```
Ordering guidance (left→right):
1. Base descriptor (example / swupdate / minimal / boot / fwu)
2. Feature fragments (example, node-red, sm, hailo, docker, lxde, preempt-rt)
3. Security & provisioning (secure-boot, otpcmd/*, rpmb-setup)
4. Tooling & reproducibility (sdk, package-lock, debian-mirror, qemu)

### 3.1 Build Cheat Sheet
| Purpose | Chain | Outputs | Notes |
|---------|-------|---------|-------|
| Full example | `kas-iot2050-example.yml` | .wic | demos + Node-RED + SM bundled |
| SWUpdate A/B | `kas-iot2050-swupdate.yml` | .wic + .swu | dual rootfs update |
| Minimal BSP | `kas/iot2050.yml` | .wic | lean base |
| Minimal parity (example) | `kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml` | .wic | matches example image |
| Example + Hailo | `kas-iot2050-example.yml:kas/opt/hailo.yml` | .wic | Hailo runtime |
| Example + LXDE + Docker | `kas-iot2050-example.yml:kas/opt/lxde.yml:kas/opt/docker.yml` | .wic | GUI + containers |
| Secure boot (sign only) | `kas-iot2050-example.yml:kas/opt/secure-boot.yml` | signed .wic | replace demo keys |
| Secure boot + provisioning | `kas-iot2050-example.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml` | enforcing image | irreversible OTP actions |
| Firmware boot chain | `kas-iot2050-boot.yml` | boot binaries | no rootfs |
| Firmware update package | `kas-iot2050-fwu-package.yml` | .tar.xz | boot chain update bundle |
| SDK | `kas-iot2050-example.yml:kas/opt/sdk.yml` | SDK tarball | cross toolchain |
| QEMU parity build | `kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml:kas-iot2050-qemu.yml` | virt .wic | emulated target |

### 3.2 Descriptor Roles
- `kas-iot2050-example.yml`: Full showcase (fastest path).
- `kas-iot2050-swupdate.yml`: A/B layout + .swu artifact.
- `kas/iot2050.yml`: Minimal base; compose features explicitly.
- `kas-iot2050-boot.yml`: Boot firmware only (sign/provision flows).
- `kas-iot2050-fwu-package.yml`: Field firmware update bundle.
- `kas-iot2050-qemu.yml`: Emulation add-on (always chained).

### 3.3 Feature Fragments
See Section 2.3 (menu toggles). Fragments map 1:1 to feature rows. Combine minimally for footprint control or for parity with example image.

### 3.4 Security, Provisioning & Reproducibility
Demo keys warning: `secure-boot.yml` ships DEMONSTRATION keys—replace before production (see [secure-boot](secure-boot.md)).
Provisioning fragments (`otpcmd/*`) are irreversible OTP actions; include exactly one when intentionally programming fuses.
Examples:
```
# Sign only
./kas-container build kas-iot2050-example.yml:kas/opt/secure-boot.yml
# Sign + provision
./kas-container build kas-iot2050-example.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml
```
Reproducibility tips:
- Add `package-lock.yml` to freeze Debian package set.
- Optionally pin mirror with `debian-mirror.yml`.
- Use clean workspace for audit / release builds.
- Consider pairing RT (`preempt-rt.yml`) with locking for deterministic kernel.

### 3.5 QEMU & Emulation
Basic run (full example):
```
./kas-container build kas-iot2050-example.yml:kas-iot2050-qemu.yml
```
Launch helper: `./scripts/host/start-qemu-iot2050.sh` (see [qemu](qemu.md)).

### 3.6 CI & Maintenance
Incremental build (reuse sstate): `./kas-container build <chain>`
Aggressive clean: `./kas-container --isar clean`
CI guidelines:
- Use explicit chains (avoid interactive menu in automation).
- Cache `downloads/` & `sstate-cache/` between jobs.
- Split secure-boot signing and provisioning into separate workflows.
- Run doc/link checks early for fast failure.
- Add `package-lock.yml` (and optional mirror) for release determinism.
- Verify feature flags: `bitbake -e iot2050-image-example | grep IOT2050_.*_SUPPORT`

## 4. Legacy Fragment Mapping (Reference)
Historic fragments (removed) and their modern equivalents:

| Removed Fragment | Replacement / Action |
|------------------|----------------------|
| `eio.yml` | Use `sm.yml` (SM/EIO now unified) |
| `module.yml` | Combine `sm.yml` + other feature fragments as needed |
| `no-node-red.yml` | Simply omit `node-red.yml` when using minimal base |

Rationale & migration detail: see
[layer-architecture](layer-architecture.md) and CHANGELOG.

## 5. Related
- [layer-architecture](layer-architecture.md)
- [maintenance](maintenance.md)
- [swupdate](swupdate.md)
- [secure-boot](secure-boot.md)
- [sdk](sdk.md)
- [fragment-catalog](fragment-catalog.md)
