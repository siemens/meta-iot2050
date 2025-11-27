# META-IOT2050
[![Build](https://github.com/siemens/meta-iot2050/actions/workflows/main.yml/badge.svg)](../../actions)
[![Links](https://github.com/siemens/meta-iot2050/actions/workflows/link-check.yml/badge.svg)](../../actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](COPYING.MIT)
[![Docs](https://img.shields.io/badge/docs-index-green)](doc/README.md)

_Applies to version: v1.6.0+_

This [Isar](https://github.com/ilbers/isar) layer contains recipes,
configuration, and other artifacts specific to the Debian-based IOT2050
product. It is accompanied by a lean core BSP and modular, opt-in layers plus
KAS fragments for feature and variant enablement (e.g., Node-RED, examples, SM,
Hailo AI, etc.).

For the complete architecture rationale and migration guide, see:
[layer-architecture](doc/layer-architecture.md).

## Prerequisites

Before building the system, you will need to install Docker on the build host.
For example, under Debian Linux:
```sh
sudo apt install docker.io
```

If you want to run Docker as a non-root user, you need to add your user to the
`docker` group:
```sh
sudo usermod -aG docker $USER   # may need to re-login after
```

## Quick Start

Interactive menu:
```sh
./kas-container menu
```

Or use `kas-container build`:
```sh
# Example image (includes demos, Node-RED, SM)
./kas-container build kas-iot2050-example.yml
```

More composition patterns: [build-config §3](doc/build-config.md#3-manual-composition)

After the build completes, the final image is located at:
`build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic`

To clean the build result:
```sh
./kas-container --isar clean
```

For a more detailed reference, please visit [build-config](doc/build-config.md).

## Deploy

### Booting the image from an SD card
Under Linux, insert an unused SD card. Assuming the SD card is assigned the
device `/dev/mmcblk0`, use `dd` to copy the image to it. For example:
```sh
sudo dd if=build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic \
    of=/dev/mmcblk0 bs=4M oflag=sync
```

Alternatively, install the `bmap-tools` package and run the following command,
which is generally faster and safer:
```sh
sudo bmaptool copy build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic /dev/mmcblk0
```

The example image starts with the IP `192.168.200.1` preconfigured on the first
Ethernet interface and uses DHCP on the other. You can use SSH to connect to
the system.

The BSP image does not configure the network. If you want to SSH into the
system, you can use the root terminal via UART to configure the IP address
using `ifconfig` and then connect via SSH.

**NOTE**: The default username is `root`. You are required to change the
default password upon first login.

### Installing the image on the eMMC (IOT2050 Advanced only)

During the very first boot of the image from an SD card or USB stick, you can
request installation to the eMMC. To do this, press the **USER button** while
the status LED is blinking orange during that first boot. Hold the button for
at least 5 seconds to start the installation.

**NOTE**: All content on the eMMC will be overwritten by this procedure!

The ongoing installation is signaled by a fast-blinking status LED. Wait for
several minutes until the LED stops blinking and the device reboots to the eMMC.
You can safely remove the SD card or USB stick at that point.

The installation can also be triggered automatically by creating the file
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
| Type / Feature | Default Contents / Purpose | How to Enable / Build | Extends With |
|----------------|-----------------------------|-----------------------|--------------|
| 🧩 Example image | Demos, Node-RED, SM variant bundled | `kas-iot2050-example.yml` | Hailo, LXDE, Docker, SDK, secure boot, QEMU |
| 🧩 Example image (SWUpdate A/B) | Example image + dual rootfs (A/B) | `kas-iot2050-swupdate.yml` | Same as example (larger footprint) |
| 🧩 Example image (minimal HW enablement) | Core BSP only; lean baseline | `kas/iot2050.yml` | `example.yml`, `node-red.yml`, `sm.yml`, others |
| 🧩 Boot firmware descriptor | TF-A, OP-TEE, U-Boot, SPL artifacts (no rootfs) | `kas-iot2050-boot.yml` | Secure boot (signing), provisioning |
| 🧩 Firmware update package | Boot chain update bundle (.tar.xz) for field updates | `kas-iot2050-fwu-package.yml` | N/A |
| QEMU descriptor | Emulated target config | Chain `:kas-iot2050-qemu.yml` after image | Adds on top of minimal or example |
| ✅ Example demos (fragment) | Reference apps & sample content | [`example.yml`](kas/opt/example.yml) or implicit | Combine with minimal image |
| ✅ Node-RED (fragment) | Flow runtime + curated nodes | [`node-red.yml`](kas/opt/node-red.yml) or implicit | Combine with minimal image |
| ✅ SM variant (fragment) | Sensors, extended IO services | [`sm.yml`](kas/opt/sm.yml) or implicit | Combine with minimal image |
| ➕ Hailo AI (fragment) | Hailo8 runtime & integration | [`hailo.yml`](kas/opt/hailo.yml) | Demos, minimal, example |
| ➕ LXDE desktop (fragment) | Lightweight desktop environment | [`lxde.yml`](kas/opt/lxde.yml) | GUI builds (example/minimal) |
| ➕ Docker / containers (fragment) | Container runtime & helpers | [`docker.yml`](kas/opt/docker.yml) | Example/minimal variants |
| ➕ SDK (fragment) | Cross-toolchain + sysroot | [`sdk.yml`](kas/opt/sdk.yml) or menu | Any image variant |
| ➕ QEMU (fragment usage) | Emulation add-on (alternate view) | `:kas-iot2050-qemu.yml` | Minimal or example builds |

See also composition reference: [build-config](doc/build-config.md#22-image-types-choices--glossary).

*Note:* Boot firmware & firmware update descriptors build only boot chain
components (no rootfs image). Combine image descriptors separately when you
need full system images.

Additional infrastructure / reproducibility / provisioning fragments (RT
kernel, package locking, RPMB setup, upstream kernel, mirror override): see
[Fragment Catalog](doc/fragment-catalog.md).

## Documentation

Index landing page: [docs index](doc/README.md)

## License

MIT – see [COPYING.MIT](COPYING.MIT)