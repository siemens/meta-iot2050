# QEMU Emulation Guide
_Applies to version: v1.6.0+_

> TL;DR: Build with `kas-iot2050-qemu.yml` (after either minimal example or
> full example descriptor), then run `./scripts/host/start-qemu-iot2050.sh`; 
> add fragments to layer in demos or features.

## 1. Build QEMU Image
To boot IOT2050 image from qemu, you need a customized image for proper booting.
Please use kas menu with the following command and select qemu image for target build
with example image or example image with swupdate support

```shell
./kas-container menu
```

Or, choose a starting descriptor:
```
# Full example image in QEMU
./kas-container build kas-iot2050-example.yml:kas-iot2050-qemu.yml

# Example image (minimal HW enablement) in QEMU
./kas-container build kas/iot2050.yml:kas-iot2050-qemu.yml
# Example image (minimal HW enablement) + demos + Node-RED + SM in QEMU
./kas-container build kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml:kas-iot2050-qemu.yml
```

## 2. Run
Then below command can be used to boot qemu image on a platform that
qemu-system-aarch64 is installed.

Run qemu:
```
/bin/sh scripts/host/start-qemu-iot2050.sh
```

Limitations: Reduced peripherals, altered device tree, performance
differences, no real watchdog, single Ethernet.

## 3. Related
- [maintenance](maintenance.md)

