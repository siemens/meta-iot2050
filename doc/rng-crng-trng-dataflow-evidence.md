# RNG Architecture and Evidence (IOT2050)

Date: 2026-07-30

## 1. Current Scheme vs target commit df8acb49

The current configuration matches the intent of commit df8acb49 (route Linux hwrng through OP-TEE and disable direct normal-world TRNG drivers).

- Linux config enables OP-TEE HWRNG and disables direct drivers:
  - `CONFIG_HW_RANDOM_OPTEE=y`
  - `# CONFIG_HW_RANDOM_OMAP is not set`
  - `# CONFIG_HW_RANDOM_ARM_SMCCC_TRNG is not set`
- OP-TEE config keeps hardware RNG export explicit:
  - `CFG_WITH_SOFTWARE_PRNG=n`
  - `CFG_HWRNG_PTA=y`
  - `CFG_HWRNG_QUALITY=1024`
- U-Boot secure boot config enables OP-TEE RNG path:
  - `CONFIG_DM_RNG=y`
  - `CONFIG_RNG_OPTEE=y`

## 2. Data Flow Diagram

### 2.1 Mermaid diagram

```mermaid
flowchart TD
    A[Applications
SSH TLS Node-RED WebUI] --> B[getrandom API
or system RNG APIs]
    B --> C[Linux random subsystem]
    C --> D[CRNG CSPRNG output]
    D --> E1[/dev/urandom]
    D --> E2[/dev/random]

    H1[Optional direct consumer] --> H2[/dev/hwrng]
    H2 --> H3[hwrng core thread]
    H3 --> H4[optee-rng driver]
    H4 --> H5[OP-TEE HWRNG PTA]
    H5 --> H6[Secure world TRNG
SA2UL EIP76]

    H3 --> R1[add_hwgenerator_randomness]
    R1 --> C
```

### 2.2 ASCII fallback diagram

```text
Applications (SSH/TLS/Node-RED/WebUI)
            |
            v
   getrandom()/system RNG APIs
            |
            v
   Linux random subsystem  --->  CRNG output  ---> /dev/urandom, /dev/random
            ^
            |
 add_hwgenerator_randomness()  <--- hwrng core thread <--- /dev/hwrng
                                                |
                                                v
                                           optee-rng
                                                |
                                                v
                                        OP-TEE HWRNG PTA
                                                |
                                                v
                                   Secure-world TRNG (SA2UL/EIP76)
```

## 3. Evidence (kernel docs + code)

### 3.1 HWRNG feeds kernel entropy pool

Kernel documentation states rng-tools use `/dev/hwrng` to fill the kernel entropy pool, and that pool backs `/dev/urandom` and `/dev/random`:

- `Documentation/admin-guide/hw_random.rst`:
  - line 21: "Those tools use /dev/hwrng to fill the kernel entropy pool"
  - lines 22-23: pool is exported by `/dev/urandom` and `/dev/random`

### 3.2 Linux random subsystem is CRNG based

`drivers/char/random.c` explicitly describes:

- line 7: "cryptographically secure pseudorandom data"
- line 11: "Fast key erasure RNG, the \"crng\""
- lines 17-23: input pool gathers entropy; stream cipher expands for consumers

### 3.3 getrandom is primary user-space interface

`drivers/char/random.c` states:

- line 1354: "getrandom(2) is the primary modern interface into the RNG"
- line 1357+: `/dev/random` semantics
- line 1362+: `/dev/urandom` semantics

### 3.4 HWRNG data is injected into random subsystem

`drivers/char/hw_random/core.c`:

- line 509: `hwrng_fillfn` thread
- line 557: calls `add_hwgenerator_randomness(...)`

`drivers/char/random.c`:

- line 779: `add_hwgenerator_randomness()` is "for true hardware RNGs"
- line 780: credits entropy specified by caller
- line 948+: implementation mixes bytes and credits init bits

### 3.5 Current repo configs that implement this design

- Linux route to OP-TEE HWRNG:
  - `meta/recipes-kernel/linux/files/iot2050_defconfig_extra.cfg`: lines 480-483
- OP-TEE HWRNG policy:
  - `meta/recipes-bsp/optee-os/optee-os-iot2050_4.10.0.inc`: lines 27-31 and 38
- U-Boot OP-TEE RNG enablement:
  - `meta/recipes-bsp/u-boot/files/secure-boot.cfg`: lines 32-33

## 4. When does TRNG entropy injection happen, and who triggers it?

Short answer:
- It is triggered by the kernel HWRNG core worker thread, not by each
  application RNG request.

Mechanism:
1. Kernel starts/uses `hwrng_fillfn` when a current HWRNG provider is active.
2. That worker reads bytes from the current HWRNG driver (here: `optee-rng`).
3. It computes entropy credit from driver quality and read size.
4. It calls `add_hwgenerator_randomness(...)` to mix data into the random
   subsystem input pool and credit entropy.
5. The random subsystem throttles as needed and reseed logic takes effect in
   CRNG behavior.

Code evidence:
- `drivers/char/hw_random/core.c`
  - line 509: `hwrng_fillfn` worker
  - lines 533-539: read from current HWRNG
  - lines 552-553: entropy credit calculation
  - line 557: call to `add_hwgenerator_randomness(...)`
  - line 542: retry path with sleep when read fails/returns no data
- `drivers/char/random.c`
  - lines 779-781: documents `add_hwgenerator_randomness()` for true HWRNG
    and entropy credit behavior
  - lines 948-952: implementation mixes bytes and credits init bits
  - lines 957-958: throttling/sleep behavior for this path

Implication:
- User space consumers (SSH/HTTPS/TLS/Node runtime, etc.) typically consume
  CRNG via `getrandom()` (primary interface), while HWRNG acts as an entropy
  source path rather than a per-request random data backend.

## 5. Answers to common review questions

### Is CRNG a TRNG?
No. CRNG is a cryptographic pseudorandom generator in the kernel. TRNG/HWRNG is a hardware entropy source.

### Does normal operation mainly use CRNG?
Yes. Typical applications use `getrandom()`/system RNG APIs. HWRNG is mainly an entropy input path to seed/reseed the kernel random subsystem.

### Can applications directly access HWRNG?
Yes, via `/dev/hwrng`, but this is usually not the preferred default path for normal application randomness needs.
