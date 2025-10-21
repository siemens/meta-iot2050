# Secure Boot & TPM / fTPM
_Applies to version: v1.6.0+_

> TL;DR: Add `secure-boot.yml`, replace demo keys, provision OTP hash,
> optionally enable fTPM + encrypted partitions, then increment
> `FIRMWARE_SECURE_VER` for anti-rollback.

## 1. Secure Boot Build Phases

Secure boot is a two-phase process:
1. Signing & layout (adds measured/signed artifacts, verity, encryption).
2. OTP provisioning (burns public key hash / enables enforcement / optional
	 key switch). Phase 2 is irreversible on production hardware.

### 1.1 Signing Only (no OTP changes yet)
Use this while developing or validating content signing:
```
./kas-container build \
	kas-iot2050-example.yml:kas/opt/secure-boot.yml
```
Result: Images are signed with DEMO keys; secure boot is NOT enforced until an
OTP provisioning fragment is included (or you program OTPs externally).

### 1.2 Signing + Provisioning (enforce secure boot)
Append exactly one provisioning fragment from `kas/opt/otpcmd/`:
```
./kas-container build \
	kas-iot2050-example.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml
```
Common provisioning variants (choose one):
```
...:kas/opt/otpcmd/key-provision-keys-only.yml       # Program hashes only
...:kas/opt/otpcmd/key-provision-enabling-only.yml   # Enable if hashes already present
...:kas/opt/otpcmd/key-provision-3keys.yml           # Program all key slots
...:kas/opt/otpcmd/key-switch.yml                    # Switch to next key
...:kas/opt/otpcmd/key-switch-2to3.yml               # Specific slot transition
```
SWUpdate A/B example with provisioning:
```
./kas-container build \
	kas-iot2050-swupdate.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml
```
Firmware (boot-only) provisioning build:
```
./kas-container build \
	kas-iot2050-boot.yml:kas/opt/secure-boot.yml:kas/opt/otpcmd/key-provision.yml
```

Adds (signing phase):
- Signing of U-Boot & unified kernel image
- dm-verity read-only rootfs + encrypted /home & /var (LUKS2)
- Demonstration keys (DO NOT use for production)
Provisioning phase additionally: programs OTP / enables enforcement / optional
key rotation per selected fragment.

## 2. Key Material
Location (pseudo):
```
meta/recipes-bsp/secure-boot-otp-provisioning/files/keys/
```
Replace demo keys for production. Maintain offline storage and documented
rotation.

## 3. OTP Provisioning Overview
Provisioning fragments (`kas/opt/otpcmd/*.yml`) embed one-time commands for:
- Public key hash programming
- Secure boot enabling
- Key switching (rollback / rotation)

Rules:
- Include at most one provisioning fragment per build chain.
- NEVER mix a provisioning fragment into routine CI builds—use a dedicated
	controlled environment.
- Review the fragment’s embedded script before running on production boards.
- For staged workflows: first do a signing-only build, verify boot, then run a
	provisioning build.

## 4. fTPM (OP-TEE based)
Included via secure boot profile when required. Provides TPM services over
TEE – confirm device nodes and `tpm2-tools` functionality:
```
tpm2_getrandom 8
```

## 5. Anti-Rollback Version
Set `FIRMWARE_SECURE_VER` (0–127) to increment trusted version.

## 6. Verification Checklist & Commands
Order: verify signing artifacts → OTP status → rootfs protection → TPM (if used)
```
sbverify --list /boot/efi/EFI/Linux/<signed-kernel>.efi
fw_printenv secure_boot
mount | grep verity
```

## 7. Production Checklist
- Replace demo keys
- Lock away private keys (HSM preferred)
- Pin `FIRMWARE_SECURE_VER` progression policy
- Document key rotation and disaster recovery
 - Maintain signed artifact manifest & reproducible build inputs (snapshot)

## 8. Related
- [swupdate](swupdate.md)
- [maintenance](maintenance.md)

