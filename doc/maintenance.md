# Maintenance & Firmware Operations
_Applies to version: v1.6.0+_

> TL;DR: Flash `.wic` (prefer `bmaptool`), configure or note default
> networking, optionally install to eMMC via USER button, update firmware with
> `iot2050-firmware-update`, and adapt/restore the U-Boot environment as needed.

## Flashing Images
There are two primary methods for flashing the `.wic` image file to an SD card or
other storages.

### Using `bmaptool` (Recommended)
For the fastest and safest flashing, use `bmaptool`. This tool provides
better performance and verifies the written data.
```sh
sudo bmaptool copy <image>.wic /dev/mmcblk0
```

### Using `dd`
Alternatively, you can use the standard `dd` utility. This method is
more basic but universally available.
```sh
sudo dd if=<image>.wic of=/dev/mmcblk0 bs=4M oflag=sync status=progress
```

## Boot Networking
- **Example image**: static `192.168.200.1` on the first Ethernet port + DHCP
  on the second interface.
- **Base BSP image**: no network preconfigured (must be configured manually
  via the UART console).

**Credentials (default)**: user `root` (no separate password-protected user);
you will be prompted to change the password on first login. This should be
done immediately for any network-connected deployment.

## eMMC Installation
On the very first boot from an SD card, you can trigger an installation to the
internal eMMC. Hold the **USER button** while the status LED blinks orange
(this is the first-boot window) for at least 5 seconds to begin.

**LED states** (during installation phase):
- Slow orange blink: First-boot window (you can trigger the install now).
- Fast blink: eMMC copy is in progress (do **NOT** power off).
- Solid / reboot: Install finished (the device will reboot automatically).

**WARNING**: All existing eMMC content will be overwritten.

To trigger this automatically, create a flag file before booting:
```sh
touch /etc/install-on-emmc
```

## Firmware Update Tool
To apply a firmware update package from the running system:
```sh
iot2050-firmware-update /usr/share/iot2050/fwu/IOT2050-FW-Update-PKG-<Version>.tar.xz
```

## Selecting Boot Device (Temporary Override)
In the U-Boot serial console, you can temporarily change the boot device:
```
=> setenv boot_targets mmc0
=> run distro_bootcmd
```

## Restoring U-Boot Environment
To restore the bootloader environment to its default state:
```sh
fw_setenv -f /etc/u-boot-initial-env
```

### Automatic Environment Adaptation & Watchdog
During the very first boot after flashing, the `patch-u-boot-env.service`
adjusts the bootloader environment. This ensures the correct root filesystem
slot is selected and, for SWUpdate images, prepares A/B handling.

It also enables the hardware watchdog in U-Boot with a 60-second timeout by
default. This ensures that a hang during early userspace brings the system
back under watchdog control.

If you need to re-trigger that logic (e.g., after manual environment edits),
reset the environment (see above) and reboot; the service will run again if
its marker conditions are unmet.

**Note**: For SWUpdate (A/B) images, the adapted environment cooperates with
EFI Boot Guard to select the correct inactive slot and to arm rollback
protection until `complete_update.sh` marks the update as successful.

