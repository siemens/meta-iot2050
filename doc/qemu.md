# QEMU Emulation Guide
_Applies to version: v1.6.0+_

> TL;DR: Build with `kas-iot2050-qemu.yml` (chained after a minimal or full
> example descriptor), then run `./scripts/host/start-qemu-iot2050.sh`.
> Add other fragments to layer in demos or features.

## Build a QEMU-compatible Image
To boot an IOT2050 image with QEMU, you need a customized image. You can
generate one using the interactive menu or by manually chaining the QEMU
descriptor.

Using the menu:
```sh
./kas-container menu
```
In the menu, select the QEMU target along with an image base like the
example image.

Or, manually chain the fragments. Choose a starting descriptor:
```sh
# Full example image in QEMU
./kas-container build kas-iot2050-example.yml:kas-iot2050-qemu.yml

# Minimal base image in QEMU
./kas-container build kas/iot2050.yml:kas-iot2050-qemu.yml

# Minimal base + demos + Node-RED + SM in QEMU
./kas-container build kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml:kas-iot2050-qemu.yml
```

## Run the Emulated Image
A helper script is provided to launch QEMU with the correct parameters.
This requires `qemu-system-aarch64` to be installed on the host.

Run QEMU:
```sh
./scripts/host/start-qemu-iot2050.sh
```

**Limitations**: Emulation provides reduced peripherals, uses an altered device
tree, has performance differences from real hardware, lacks a real watchdog,
and only exposes a single Ethernet interface.

## Related
- [maintenance](maintenance.md)

