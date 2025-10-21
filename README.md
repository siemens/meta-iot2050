# META-IOT2050  
[![Build](https://github.com/siemens/meta-iot2050/actions/workflows/main.yml/badge.svg)](../../actions)
[![Links](https://github.com/siemens/meta-iot2050/actions/workflows/link-check.yml/badge.svg)](../../actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](COPYING.MIT)
[![Docs](https://img.shields.io/badge/docs-index-green)](doc/README.md)

_Applies to version: v1.6.0+_

This [Isar](https://github.com/ilbers/isar) layer contains recipes,
configuration and other artifacts that are specific to  Debian-based IOT2050
product. It is accompanied by a lean core BSP and modular, opt‑in layers plus
KAS fragments for feature and variant enablement (e.g. Node-RED, examples, SM
, Hailo AI, etc.).

For the complete architecture rationale and migration guide see:
[layer-architecture](doc/layer-architecture.md).

Recent changes and migration notes: refer to [CHANGELOG](CHANGELOG.md).

## Prerequisites

Before building the system, you will need to install docker on build host. For
For the complete architecture rationale and migration guide see:
example under Debian Linux:
```shell
sudo apt install docker.io
```

If you want to run docker as non-root user then you need to add your user to the
docker group:
```shell
sudo usermod -aG docker $USER   # may need to re-login after
```

## Quick Start

Interactive menu:

```shell
./kas-container menu
```

Or use `kas-container build`:
```shell
# Example image (includes demos, Node-RED, SM)
./kas-container build kas-iot2050-example.yml
```

More composition patterns: [build-config §3](doc/build-config.md#3-manual-composition)

After the build completed, the final image is under:

```text
build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic
```

Clean build result:

```shell
./kas-container --isar clean
```

For more detailed reference please visit [build-config](doc/build-config.md).

## Deploy

### Booting the image from SD card
Under Linux, insert an unused SD card. Assuming the SD card takes device
/dev/mmcblk0, use dd to copy the image to it. For example:

```shell
$ sudo dd if=build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic \
          of=/dev/mmcblk0 bs=4M oflag=sync
```

Alternatively, install the `bmap-tools` package and run the following command
which is generally faster and safer:

```shell
$ sudo bmaptool copy build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic /dev/mmcblk0
```

The example image starts with the IP 192.168.200.1 preconfigured on the first
Ethernet interface, and use DHCP at another. You can use ssh to connect to the
system.

The BSP image does not configure the network. If you want to ssh into the
system, you can use the root terminal via UART to ifconfig the IP address and
use that to ssh in.

NOTE: To login, the default username and password is `root`. And you are
required to change the default password when first login.

### Installing the image on the eMMC (IOT2050 Advanced only)

During the very first boot of the image from an SD card or USB stick, you can
request the installation to the eMMC. For that, press the USER button while
the status LED is blinking orange during that first boot. Hold the button for
at least 5 seconds to start the installation.

NOTE: All content of the eMMC will be overwritten by this procedure!

The ongoing installation is signaled by a fast blinking status LED. Wait for
several minutes until the LED stops blinking and the device reboots to the eMMC.
You can safely remove the SD card or USB stick at that point.

The installation can also be triggered automatically by creating the file
`/etc/install-on-emmc` on the vanilla image by mounting it under Linux and
executing, e.g., `touch <mountpoint>/etc/install-on-emmc`.

### Updating the U-Boot firmware

Starting from V01.05.x, the updated firmware tarball is integrated into the
`/usr/share/iot2050/fwu/` directory by default. To update the U-Boot firmware,
execute the following command:

```sh
iot2050-firmware-update /usr/share/iot2050/fwu/IOT2050-FW-Update-PKG-<Version>.tar.xz
```

### Selecting a boot device

By default, the boot loader will pick the first bootable device. If that device
may no longer fully start, you can select an alternative boot device in the
U-Boot shell. Attach a USB-UART adapter to X14, connect it to a host PC and open
a terminal program on that port. Reset the device and interrupt the boot when it
counts down ("Hit any key to stop autoboot"). Then type

```shell
=> setenv boot_targets mmc0
=> run distro_bootcmd
```

to boot from the microSD card. Use `usb0` for the first USB mass storage device.

NOTE: This selection is not persistent. The boot loader will fall back to its
default boot order after reset.

## Images & Features Matrix
Legend: ✅ = implicit / already included in example image & SWUpdate images, ➕ = optional fragment, 🧩 = descriptor (top-level KAS file)

| Type / Feature | Default Contents / Purpose | How to Enable / Build | Extends With | Docs |
|----------------|-----------------------------|-----------------------|--------------|------|
| 🧩 Example image | Demos, Node-RED, SM variant bundled | `kas-iot2050-example.yml` | Hailo, LXDE, Docker, SDK, secure boot, QEMU | [Architecture](doc/layer-architecture.md) |
| 🧩 Example image (SWUpdate A/B) | Example image + dual rootfs (A/B) | `kas-iot2050-swupdate.yml` | Same as example (larger footprint) | [SWUpdate](doc/swupdate.md) / [Details](#swupdate) |
| 🧩 Example image (minimal HW enablement) | Core BSP only; lean baseline | `kas/iot2050.yml` | `example.yml`, `node-red.yml`, `sm.yml`, others | [Build Config](doc/build-config.md#22-image-types-choices--glossary) / [SM/EIO](#sm--eio-support) |
| 🧩 Boot firmware descriptor | TF-A, OP-TEE, U-Boot, SPL artifacts (no rootfs) | `kas-iot2050-boot.yml` | Secure boot (signing), provisioning | [Maintenance](doc/maintenance.md#firmware) |
| 🧩 Firmware update package | Boot chain update bundle (.tar.xz) for field updates | `kas-iot2050-fwu-package.yml` | N/A | [Maintenance](doc/maintenance.md#firmware) |
| QEMU descriptor | Emulated target config | Chain `:kas-iot2050-qemu.yml` after image | Adds on top of minimal or example | [QEMU](doc/qemu.md) / [Details](#qemu-emulation) |
| ✅ Example demos (fragment) | Reference apps & sample content | [`example.yml`](kas/opt/example.yml) or implicit | Combine with minimal image | [Build Config](doc/build-config.md#3-manual-composition) |
| ✅ Node-RED (fragment) | Flow runtime + curated nodes | [`node-red.yml`](kas/opt/node-red.yml) or implicit | Combine with minimal image | [meta-node-red](meta-node-red/README.md) / [Security](#security) |
| ✅ SM variant (fragment) | Sensors, extended IO services | [`sm.yml`](kas/opt/sm.yml) or implicit | Combine with minimal image | [meta-sm](meta-sm/README.md) / [SM/EIO](#sm--eio-support) |
| ➕ Hailo AI (fragment) | Hailo8 runtime & integration | [`hailo.yml`](kas/opt/hailo.yml) | Demos, minimal, example | [meta-hailo](meta-hailo/README.md) / [Hailo8](#hailo8-ai-accelerator) |
| ➕ LXDE desktop (fragment) | Lightweight desktop environment | [`lxde.yml`](kas/opt/lxde.yml) | GUI builds (example/minimal) | [Build Config](doc/build-config.md) |
| ➕ Docker / containers (fragment) | Container runtime & helpers | [`docker.yml`](kas/opt/docker.yml) | Example/minimal variants | [Build Config](doc/build-config.md) |
| ➕ SDK (fragment) | Cross-toolchain + sysroot | [`sdk.yml`](kas/opt/sdk.yml) or menu | Any image variant | [SDK](doc/sdk.md) / [Details](#sdk-toolchain) |
| ➕ Secure boot (fragment) | Signing only unless a single provisioning fragment appended | [`secure-boot.yml`](kas/opt/secure-boot.yml) (+ one `otpcmd/*` to enforce) | Example/minimal/SWUpdate | [Secure Boot](doc/secure-boot.md) / [Security](#security) |
| ➕ QEMU (fragment usage) | Emulation add-on (alternate view) | `:kas-iot2050-qemu.yml` | Minimal or example builds | [QEMU](doc/qemu.md) / [Details](#qemu-emulation) |

See also composition reference: [build-config](doc/build-config.md#22-image-types-choices--glossary).

*Note:* Boot firmware & firmware update descriptors build only boot chain
components (no rootfs image). Combine image descriptors separately when you
need full system images.

Additional infrastructure / reproducibility / provisioning fragments (RT
kernel, package locking, RPMB setup, upstream kernel, mirror override): see
[Fragment Catalog](doc/fragment-catalog.md).

## Versioning & Changelog

Semantic Versioning. Migration notes & changes: [CHANGELOG](CHANGELOG.md). Always review the `Migration` section before upgrading.

## Documentation

Index landing page: [docs index](doc/README.md)

## License

MIT – see [COPYING.MIT](COPYING.MIT)