# meta-hailo - Support for HAILO NPU chips

This repo provides recipes to build the kernel and userspace drivers and utilities
(V4.18) for the Hailo-8 NPU chip.
This includes the following main components:

- hailo-pci (OSS kernel module)
- hailo-firmware (proprietary firmware for hailo8 chip)
- hailort (Userspace API)
  - hailortcli (tool)
  - hailort (service)
  - libhailort (c library)
  - libhailort-dev (dev package)
  - python3-hailort (python library)

> Note: `numpy==1.23.3` is preinstalled. Please do not upgrade it, as
> `hailort v4.18.0` requires this specific version. Upgrading `numpy` may cause
> `pyhailort` to fail to execute.

## Versioning

This layer is versioned according to the major hailo driver version.
Note, that the kernel ABI is not stable and by that the version of the
userspace components need to perfectly match the version of the firmware
and the kernel module.
