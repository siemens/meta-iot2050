# TRNG Validation Report (IOT2050)

Date: 2026-07-24 (UTC)
Target: root@192.168.200.1
Image: IOT2050 Debian Example Image
Kernel: 6.12.94-cip26
Build ID: V01.06.01-85-gf4a38d2d

## Scope
Validate that `/dev/hwrng` is routed through OP-TEE and remains usable under load.

## Commands and Results

### 1) Basic system and RNG provider
- `uname -a`
- `cat /etc/os-release`
- `ls -l /dev/hwrng`
- `cat /sys/class/misc/hw_random/rng_available`
- `cat /sys/class/misc/hw_random/rng_current`

Observed:
- `/dev/hwrng` exists.
- `rng_available`: `optee-rng tpm-rng-0 none`
- `rng_current`: `optee-rng`

Conclusion:
- HWRNG path is active and currently selected provider is OP-TEE RNG.

### 2) Boot/runtime logs (RNG/OP-TEE)
- `dmesg | grep -Ei 'optee|optee-rng|hwrng|rng|sa2ul|eip76' | tail -n 120`

Observed key lines:
- `optee: revision 4.10`
- `optee: dynamic shared memory is enabled`
- `optee: initialized driver`
- `random: crng init done`

Conclusion:
- OP-TEE runtime is active on this image and kernel sees OP-TEE stack initialized.

### 3) Functional read test (1 MiB)
- `dd if=/dev/hwrng of=/tmp/hwrng.bin bs=4096 count=256 status=none`
- `sha256sum /tmp/hwrng.bin`

Observed:
- `/tmp/hwrng.bin` generated successfully (1.0 MiB)
- SHA256: `c4e7efb40d13e6acbb0ecdf15c7b9c4d74a5cf86b78b2a8fb1b3c347cef994bd`

Conclusion:
- Basic random read from `/dev/hwrng` works.

### 4) Single-stream throughput (64 MiB)
- `dd if=/dev/hwrng of=/dev/null bs=4096 count=16384 status=none`

Observed:
- Completed in about `182` seconds.

Approx throughput:
- `64 MiB / 182 s ~= 0.352 MiB/s` (about `360 KiB/s`).

Conclusion:
- Throughput is limited but stable, consistent with OP-TEE mediated RNG path.

### 5) Controlled parallel stability test (4 workers, each 4 MiB)
- 4 concurrent workers, each:
  - `timeout 90 dd if=/dev/hwrng of=/dev/null bs=4096 count=1024 status=none`

Observed:
- `worker1:OK elapsed_sec=48`
- `worker2:OK elapsed_sec=48`
- `worker3:OK elapsed_sec=48`
- `worker4:OK elapsed_sec=48`
- Post-check: `rng_current` remains `optee-rng`

Conclusion:
- Parallel bounded reads succeeded without provider fallback.

## Overall Assessment
- PASS: OP-TEE RNG route is effective and selected (`rng_current=optee-rng`).
- PASS: Functional and bounded parallel reads are stable.
- NOTE: Throughput is relatively low, expected for OP-TEE mediated access.

## Typical BSP Component Validation (Current Round)

This section summarizes typical checks for OP-TEE, U-Boot, and Linux.
Only items already verified in this round are marked as PASS.

### A) OP-TEE (verified in this round)

1) OP-TEE driver is initialized in Linux runtime
- Command:
  - `dmesg | grep -Ei 'optee|optee-rng|hwrng|rng|sa2ul|eip76' | tail -n 120`
- Observed:
  - `optee: revision 4.10`
  - `optee: dynamic shared memory is enabled`
  - `optee: initialized driver`
- Status: PASS

2) OP-TEE-backed HWRNG provider is selected
- Command:
  - `cat /sys/class/misc/hw_random/rng_available`
  - `cat /sys/class/misc/hw_random/rng_current`
- Observed:
  - `rng_available`: `optee-rng tpm-rng-0 none`
  - `rng_current`: `optee-rng`
- Status: PASS

### B) Linux Kernel (verified in this round)

1) Running kernel version matches target update line
- Command:
  - `uname -a`
- Observed:
  - `Linux ... 6.12.94-cip26 ...`
- Status: PASS

2) HWRNG functionality and stability
- Commands:
  - `dd if=/dev/hwrng of=/tmp/hwrng.bin bs=4096 count=256 status=none`
  - `dd if=/dev/hwrng of=/dev/null bs=4096 count=16384 status=none`
  - 4-way bounded parallel read (4 MiB each)
- Observed:
  - 1 MiB sample read success
  - 64 MiB single-stream read success
  - 4 workers all `OK`
- Status: PASS

### C) U-Boot (template for your follow-up comparison)

The following are typical checks but were not fully captured in this runtime
round. Keep this as a checklist and fill in based on your next board run.

1) U-Boot version/banner check
- Command:
  - Capture serial log at boot and verify U-Boot 2026.07 banner.
- Expected:
  - Banner/version corresponds to updated U-Boot.
- Status: TODO

2) Secure boot / EFI path sanity (if enabled on image)
- Command:
  - Capture U-Boot boot log around EFI hand-off and secure boot messages.
- Expected:
  - No regression in EFI hand-off.
- Status: TODO

3) U-Boot RNG/OP-TEE path sanity (if observable in boot log)
- Command:
  - Capture boot log and search for OP-TEE / RNG related init strings.
- Expected:
  - No RNG-related errors during boot stage.
- Status: TODO

### D) Optional security service checks (template)

1) TPM/fTPM presence
- Command:
  - `dmesg | grep -Ei 'tpm|ftpm'`
  - `ls /dev/tpm*`
- Status: TODO

2) RPMB / StMM related services (when applicable)
- Command:
  - `dmesg | grep -Ei 'rpmb|stmm|efi mm'`
- Status: TODO

## Repro Command Snippets

```sh
# Provider check
cat /sys/class/misc/hw_random/rng_available
cat /sys/class/misc/hw_random/rng_current

# 1 MiB functional read
dd if=/dev/hwrng of=/tmp/hwrng.bin bs=4096 count=256 status=none
sha256sum /tmp/hwrng.bin

# 64 MiB single-stream timing
START=$(date +%s)
dd if=/dev/hwrng of=/dev/null bs=4096 count=16384 status=none
END=$(date +%s)
echo $((END-START))

# Controlled parallel test
for i in 1 2 3 4; do
  (timeout 90 dd if=/dev/hwrng of=/dev/null bs=4096 count=1024 status=none && echo worker${i}:OK || echo worker${i}:FAIL) &
done
wait
cat /sys/class/misc/hw_random/rng_current
```
