# BSP Upgrade: U-Boot 2026.07, OP-TEE 4.10.0, Linux 6.12.94-cip26, Secure Boot Alignment, and OP-TEE-routed HWRNG

## Summary
This PR updates the IOT2050 BSP stack across bootloader, TEE, kernel, and image integration layers, with a focus on version alignment, secure boot path stability, and secure random source routing through OP-TEE.

## Why
- Align core BSP components to current maintained versions.
- Ensure secure-world ownership of hardware RNG and avoid normal-world direct contention.
- Keep secure boot and EFI boot behavior stable after version bumps.
- Scope efibootguard config behavior correctly between Example and SWUpdate image paths.

## Included Commits
- 0be319dd meta-example: Scope efibootguard config parts
- f4a38d2d linux-iot2050: Disable 1.8V signaling on sdhci1
- 9ec56c68 linux-iot2050: Update to v6.12.94-cip26
- 570910f7 linux-iot2050: Route hwrng through OP-TEE
- 454105d5 u-boot-iot2050: Update to v2026.07 with K3 SPL/FDT fixes
- 44616a03 SEBoot: Bump to 1.6.3
- c1d3e044 optee-ftpm: Update to 4.10.0
- 58ac18dc optee-client: Update to 4.10.0
- c9fd21c8 u-boot-iot2050: Enable RNG
- db31e2a9 optee-os: Update to 4.10.0
- 85f4de1f iot2050-eio-webui: Correct the package-lock version

## Key Changes

### U-Boot / Early Boot
- Updated U-Boot to 2026.07 with K3 SPL/FDT fixes.
- Enabled RNG support in U-Boot with OP-TEE RNG integration path.
- Maintained secure boot compatibility and EFI hand-off behavior after upgrade.

### OP-TEE / Trusted Execution
- Updated OP-TEE OS to 4.10.0.
- Updated OP-TEE client and fTPM to 4.10.0 for stack consistency.
- Moved to secure-world TRNG handling model and pinned OP-TEE HWRNG PTA settings in recipe build arguments.

### Linux Kernel
- Updated kernel to 6.12.94-cip26.
- Routed Linux hwrng through OP-TEE.
- Disabled direct omap-rng and arm-smccc-trng access in this integration path to avoid contention.
- Set OP-TEE hwrng support as built-in for earlier availability.
- Disabled 1.8V signaling on sdhci1 per board stability requirements.

### Image Integration
- Scoped efibootguard config-part override for Example image behavior.
- Preserved SWUpdate dual BOOT partition behavior (BOOT0 and BOOT1).
- Corrected webui package-lock metadata without functional behavior change.

## Compatibility and Risk Notes
- OP-TEE-mediated hwrng has lower raw throughput than direct hardware access; this is expected by design.
- Functional randomness sourcing remains stable and suitable for entropy injection into kernel CRNG.
- No boot chain regression observed in validated image paths.

## Validation Matrix

| Area | Change Scope | Validation Method | Evidence / Checkpoints | Result |
|---|---|---|---|---|
| Boot Chain | End-to-end SEBoot -> U-Boot -> OP-TEE -> Linux integration | Cold boot and reboot cycles | No boot hang, no unexpected reset loop, system reaches userspace reliably | PASS |
| U-Boot Upgrade | U-Boot updated to 2026.07 (including K3 SPL/FDT fixes) | Boot log and version/path checks | Version/path behavior matches expected upgrade target, no boot regression observed | PASS |
| Secure Boot | Secure boot flow | Signed image boot validation | Signed image boots successfully, no authentication regression observed | PASS |
| EFI Handoff | UEFI handoff path | EFI boot path smoke checks | EFI handoff remains functional, no new warnings in normal flow | PASS |
| OP-TEE Runtime | OP-TEE updated to 4.10.0 | Runtime log verification | OP-TEE reports revision 4.10 and initializes correctly | PASS |
| OP-TEE Client | optee-client updated to 4.10.0 | User-space to TEE integration smoke checks | Client/runtime compatibility confirmed, no call-path regression | PASS |
| fTPM | optee-ftpm updated to 4.10.0 | TPM/fTPM functional smoke checks | fTPM path remains functional and compatible with updated stack | PASS |
| Kernel Upgrade | Linux updated to 6.12.94-cip26 | Version and baseline regression checks | Kernel version correct, baseline system behavior stable | PASS |
| SDHCI Change | Disable 1.8V signaling on sdhci1 | Storage initialization/regression checks | No new MMC/SD initialization regression observed | PASS |
| TRNG Routing | Linux hwrng routed via OP-TEE | sysfs + dmesg + functional/stability reads | rng_current=optee-rng, bounded reads and parallel reads pass | PASS |
| U-Boot RNG | U-Boot RNG enabled (OP-TEE path) | Boot-stage integration checks | No RNG-related errors observed in boot stage | PASS |
| meta-example | efibootguard config-part scoping | Example vs SWUpdate path comparison | Example image no longer reports false partial corruption; SWUpdate dual-part behavior preserved | PASS |
| WebUI Packaging | package-lock correction | WebUI startup/access smoke check | No startup regression observed | PASS |

## TRNG Validation Highlights
- rng_available shows optee-rng present.
- rng_current is optee-rng.
- Functional read from /dev/hwrng succeeded.
- Bounded parallel hwrng reads completed successfully with all workers passing.
- Detailed execution record is available at doc/trng-validation-2026-07-24.md.

## Reviewer Focus Areas
- Boot chain compatibility after synchronized U-Boot, OP-TEE, and Linux upgrades.
- Secure boot and EFI hand-off behavior continuity.
- Correctness of hwrng routing and provider selection through OP-TEE.
- efibootguard scoping behavior across Example and SWUpdate image variants.

## Checklist
- [x] Version upgrades applied and integrated
- [x] Secure boot path validated
- [x] EFI hand-off validated
- [x] OP-TEE runtime/client/fTPM alignment validated
- [x] Kernel hwrng path routed through OP-TEE and validated
- [x] Example vs SWUpdate efibootguard behavior validated
- [x] No critical regression observed in covered test scope
