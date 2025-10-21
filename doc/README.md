# Documentation Index

_Applies to version: v1.6.0+_

Quick entry points for the IoT2050 meta layers. Each document owns one domain; use this file or the root README for navigation.

| Topic | File | TL;DR |
|-------|------|-------|
| Layer architecture & migration | [layer-architecture](layer-architecture.md) | Modular split of core vs feature/variant layers & how to migrate. |
| SWUpdate A/B images | [swupdate](swupdate.md) | Build, flash, and update dual-rootfs images; confirm updates safely. |
| Secure boot & fTPM | [secure-boot](secure-boot.md) | Enable signature, dm-verity, encryption, OTP provisioning, anti-rollback. |
| Maintenance & operations | [maintenance](maintenance.md) | Flashing, network defaults, eMMC install, firmware tool, env adaptation. |
| SDK | [sdk](sdk.md) | Build and use cross SDK (tarball & Docker). |
| QEMU emulation | [qemu](qemu.md) | Build and run emulated image; limitations & debug tips. |
| Build configuration (menu & manual) | [build-config](build-config.md) | TUI vs manual fragment chaining and examples. |

Conventions:
- One topic per file, no duplicated procedural steps.
- Root README = high-level overview + quick start.
- This index = discovery map for deeper tasks.

See also: top-level `CHANGELOG.md` for versioned changes.
