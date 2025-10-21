# meta - IoT2050 BSP Layer

## Overview

The `meta` layer provides hardware enablement for the Siemens IoT2050 platform. This layer contains only essential components required to boot Debian on IoT2050 hardware.

## Purpose

- **Hardware enablement only** - no applications or demo components
- **Minimal bootable system** - essential packages for IoT2050 operation
- **Foundation layer** - other layers depend on this BSP layer

## Contents

### Machine Configuration
- `conf/machine/iot2050.conf` - Main machine definition
- `conf/distro/` - Distribution configurations (if any)

### Recipes
- `recipes-bsp/` - Bootloader (U-Boot) and firmware
- `recipes-kernel/` - Linux kernel and device trees
- `recipes-core/images/` - Base image recipe
- `recipes-core/packagegroups/` - Hardware package groups

### Images
- `iot2050-base-image` - Minimal bootable image with hardware support only

## Key Features

- ✅ U-Boot bootloader support
- ✅ Linux kernel with IoT2050 device trees
- ✅ Essential firmware and drivers
- ✅ SSH access for remote management
- ✅ Minimal Debian userspace

## Dependencies

- **isar** - Base Isar framework
- **cip-core** - Security and compliance features

## Build

```bash
kas build kas/iot2050-base.yml
```

## Maintainers

See top-level `MAINTAINERS` file in the repository root.

## License

MIT License - See COPYING.MIT in repository root.