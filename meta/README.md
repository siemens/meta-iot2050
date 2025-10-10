# meta - IoT2050 BSP Layer

## Overview

The `meta` layer provides the core hardware enablement for the Siemens IoT2050
platform. This layer contains only the essential components required to boot a
Debian-based OS on IoT2050 hardware.

## Scope & Purpose

- **Hardware Enablement Only**: Does not include applications, demos, or
  optional features.
- **Minimal Bootable System**: Contains only the essential packages for
  IoT2050 hardware operation.
- **Foundation Layer**: All other feature and variant layers depend on this
  core BSP layer.

## Contents

### Machine Configuration
- `conf/machine/iot2050.conf`: The main machine definition.
- `conf/distro/`: Distribution-specific configurations.

### Recipes
- `recipes-bsp/`: Bootloader (U-Boot) and firmware.
- `recipes-kernel/`: Linux kernel and device trees.
- `recipes-core/images/`: The base image recipe.
- `recipes-core/packagegroups/`: Hardware-specific package groups.

### Images
- `iot2050-base-image`: A minimal bootable image with hardware support only.

## Key Features

- ✅ U-Boot bootloader support
- ✅ Linux kernel with IoT2050 device trees
- ✅ Essential firmware and drivers
- ✅ SSH access for remote management
- ✅ Minimal Debian userspace

## Dependencies

- **isar**: The base Isar framework.
- **cip-core**: Security and compliance features.

## Build

To build the minimal base image defined in this layer:
```sh
kas build kas/iot2050.yml
```

## Maintainers

See the top-level `MAINTAINERS` file in the repository root.

## License

MIT License - See `COPYING.MIT` in the repository root.