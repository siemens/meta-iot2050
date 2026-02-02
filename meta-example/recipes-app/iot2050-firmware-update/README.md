# IOT2050 Firmware Update Tool

This document describes the `iot2050-firmware-update` command-line tool, which is
used to update the OSPI flash firmware (bootloader) on the IOT2050 device.

The tool is designed to be robust, providing features like automatic backups,
rollbacks, and U-Boot environment preservation. It also includes a security
mechanism to verify the integrity and authenticity of firmware before
installation.

## Firmware Update Package

The tool uses a `.tar.xz` compressed tarball as the standard update package.
This package must contain the following files:

- **Firmware Binary**: The bootloader image to be flashed (e.g., `iot2050-pg2-image-boot.bin`).
- **`update.conf.json`**: A JSON file that defines metadata and rules for the
  update, such as target board compatibility and version requirements.
- **`u-boot-initial-env`**: A text file containing the default U-Boot
  environment variables.
- **`firmware.bin.sig` (Optional)**: A signature file for the firmware binary,
  used for the secure update process.

## Usage

The tool provides several command-line options for different update scenarios.

### Standard Update

To perform a standard update, simply provide the path to the firmware package:

```sh
iot2050-firmware-update <firmware-package>.tar.xz
```

The tool will automatically back up the current firmware before proceeding. If the
update fails, it can be rolled back.

### Key Features and Options

- **Rollback (`-b`, `--rollback`)**:
  Rolls back to the previously backed-up firmware version.

  ```sh
  iot2050-firmware-update -b
  ```

- **Preserve U-Boot Environment (`-p`, `--preserve_list`)**:
  Preserves a comma-separated list of U-Boot environment variables during the
  update. This is useful for retaining settings like `boot_targets` and
  `watchdog_timeout_ms`.

  ```sh
  iot2050-firmware-update -p "boot_targets,watchdog_timeout_ms" <firmware-package>.tar.xz
  ```

- **Reset U-Boot Environment (`-r`, `--reset`)**:
  Resets all U-Boot environment variables to the defaults specified in the
  `u-boot-initial-env` file from the package.

- **Force Update (`-f`, `--force`)**:
  Forces the installation of a raw firmware binary file, bypassing all safety
  checks (e.g., version and board compatibility). This is a powerful feature
  intended for development and debugging purposes only. Use with extreme
  caution, as it can render the device unbootable if an incorrect or corrupt
  firmware is used.

  ```sh
  iot2050-firmware-update -f <firmware>.bin
  ```

## Secure Firmware Update

For production environments, it is critical to ensure that only trusted firmware
can be installed. The tool supports a secure update process based on RSA digital
signatures.

The core concept is:
1.  **Downstream Signing**: The firmware binary is signed offline by the
    developer or a build system using a private RSA key.
2.  **On-Device Verification**: The `iot2050-firmware-update` tool uses a
    corresponding public key, pre-installed on the device, to verify the
    firmware's signature before flashing.


### Security Model

The security of the firmware update process relies on a chain of trust established
by a public/private key pair.

```
┌─────────────────────────┐
│  Trusted Signing Key    │
│  (Your Private Key)     │
└───────────┬─────────────┘
            │ Signs firmware hash
            ▼
┌─────────────────────────┐
│  Firmware Binary        │
│  + Signature File       │
└───────────┬─────────────┘
            │ Distributed to devices
            ▼
┌─────────────────────────┐
│  IOT2050 Device         │
│  (Has Public Key)       │
│  Verifies signature     │
└─────────────────────────┘
```

### Key Management

- **Private Key:** Must be kept secret and stored securely (e.g., in an HSM or
  a secure vault). Compromise of the private key allows an attacker to sign
  malicious firmware.
- **Public Key:** Must be securely provisioned into the IOT2050 base image in
  a read-only filesystem to prevent tampering. This key establishes the chain
  of trust.


### Signing the Firmware

The signing process is performed by the "downstream" user (the developer or
organization building the final firmware). It is not performed on the IOT2050
device itself.

#### Prerequisites

- **Signing Infrastructure**: A tool or service capable of creating RSA
  signatures from a hash. This could be the `openssl` command-line tool, a
  cloud-based Key Management Service (KMS), or a Hardware Security Module (HSM).
- **RSA Key Pair**: A private key for signing and its corresponding public key
  for verification. The public key must be deployed on the IOT2050 device.

#### Generating an RSA Key Pair

If you don't have a key pair, generate one using OpenSSL:

```sh
# Generate a 4096-bit RSA private key
openssl genpkey -algorithm RSA -out private.key -pkeyopt rsa_keygen_bits:4096

# Extract the public key from the private key
openssl rsa -pubout -in private.key -out public.key
```

#### Signing Process

The fundamental signing process involves creating a digital signature of the
firmware binary's hash. While this can be done with various tools, including
Hardware Security Modules (HSMs) or other signing services, the following
example uses `openssl`.

**Example using OpenSSL:**

1.  **Calculate the SHA-512 Hash of the firmware binary**:
    ```sh
    openssl dgst -sha512 -binary -out firmware.bin.hash firmware.bin
    ```

2.  **Sign the hash with the private key**:
    ```sh
    openssl pkeyutl -sign -inkey private.key -pkeyopt digest:sha512 -in firmware.bin.hash -out firmware.bin.sig
    ```

The resulting `firmware.bin.sig` file must be added to the firmware update
package alongside the `firmware.bin` file.

### On-Device Verification

The on-device verification is triggered by the `--verify` flag.

#### Prerequisites

The public key (`public.key`) corresponding to the signing key must be installed
on the device at the following location:

`/usr/share/iot2050/fwu/public.key`

This key should be deployed to the device as part of the base OS image to ensure
it is trusted.

#### Verification Command

To run an update with signature verification, use the `--verify` flag:

```sh
iot2050-firmware-update --verify <firmware-package>.tar.xz
```

The tool will perform these steps:
1.  Extract the firmware binary and its `.sig` file from the package.
2.  Load the public key from `/usr/share/iot2050/fwu/public.key`.
3.  Use the public key to verify that the signature in the `.sig` file matches
    the calculated hash.

If the signature is valid, the update proceeds. If it is invalid, or if the
public key or signature file is missing, the tool will abort with an error,
preventing a potentially malicious or corrupt firmware from being installed.

## Terminology

- **FWU:** Firmware Update
- **HSM:** Hardware Security Module

## References

- [PKCS#1 v2.2: RSA Cryptography Standard](https://www.rfc-editor.org/rfc/rfc8017)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
