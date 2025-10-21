# Maintenance & Firmware Operations
_Applies to version: v1.6.0+_

> TL;DR: Flash `.wic` (prefer `bmaptool`), configure or note default
> networking, optional eMMC install via USER button, update firmware with
> `iot2050-firmware-update`, adapt/restore U-Boot env as needed.

## 1. Flashing Images
Prefer `bmaptool` for speed & verification:
```
sudo bmaptool copy <image>.wic /dev/mmcblk0
```

## 2. microSD Boot Networking
Example image: static 192.168.200.1 on first Ethernet + DHCP on second
interface. Base BSP image: no network preconfigured (configure manually via
UART console).

Credentials (default): user `root` (no separate password user); you will be
prompted to change the password on first login. Change it immediately for
any connected deployment.

## 3. eMMC Installation
First boot: hold USER button while status LED blinks orange (first-boot
window) for ≥5s to start installation to eMMC.
LED states (installation phase):
- Slow orange blink: first-boot window (you can trigger install)
- Fast blink: eMMC copy in progress (do NOT power off)
- Solid / reboot: install finished (device will reboot automatically)

WARNING: All existing eMMC content will be overwritten.
Automatic method:
```
touch /etc/install-on-emmc
```

## 4. Firmware Update Tool
```
iot2050-firmware-update /usr/share/iot2050/fwu/IOT2050-FW-Update-PKG-<Version>.tar.xz
```
For secure boot / RPMB provisioning ordering (e.g. adding `rpmb-setup.yml`
alongside OTP command fragments) see the ordering guidance in the Fragment
Catalog (`fragment-catalog.md`).

## 5. Selecting Boot Device (temporary override)
```
=> setenv boot_targets mmc0
=> run distro_bootcmd
```

## 6. Restoring U-Boot Environment
```
fw_setenv -f /etc/u-boot-initial-env
```

### 6.1 Automatic Environment Adaptation & Watchdog
During the very first boot after flashing, the service
`patch-u-boot-env.service` adjusts the bootloader environment so the correct
root filesystem slot is selected (and for SWUpdate images, prepares A/B
handling). It also enables the hardware watchdog in U-Boot with a 60s
timeout by default. This ensures that a hang during early userspace brings
the system back under watchdog control.

If you need to re-trigger that logic (e.g. after manual environment edits),
reset the environment (see above) and reboot; the service will run again if
its marker conditions are unmet.

Note: For SWUpdate (A/B) images the adapted environment cooperates with EFI
Boot Guard to select the correct inactive slot and to arm rollback
protection until `complete_update.sh` marks success.

## 7. Troubleshooting
| Area | Symptom | Action |
|------|---------|--------|
| Flash | Boot fails after write | Reflash via bmaptool; verify checksum |
| eMMC install | LED never stops | Check serial console for errors |
| Firmware update | Script aborts | Confirm package path & integrity |

## 8. Related
- [swupdate](swupdate.md)
- [secure-boot](secure-boot.md)

