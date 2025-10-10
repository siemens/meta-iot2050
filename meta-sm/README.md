# meta-sm – IoT2050 SM Variant Layer

_Applies to meta-iot2050 v1.6.0+ modular layout._

This layer supplies the optional SM variant user-space components and device
tree for boards equipped with the additional peripherals.

## Overview

`meta-sm` is an additive layer. It does **not** redefine a separate machine
type. Instead, the canonical Example and SWUpdate image descriptors include its
content implicitly. When using the minimal base descriptor, you can opt-in via
the `sm.yml` fragment, which sets `IOT2050_SM_SUPPORT=1`.

## Scope & Purpose

| Category | Scope |
|----------|-------|
| Sensors & IO mgmt | EIO manager, proximity / event utilities |
| Variant services | Event recording, configuration web UI integration |
| Firmware helper  | Module firmware update helper (for the signal module) |
| Device tree      | SM-specific DTB addition(s) |

## Build

SM support is enabled by default in the main example images.

**Build the full example image** (includes SM):
```sh
./kas-container build kas-iot2050-example.yml
```

**Build from the minimal base** and add SM support:
```sh
./kas-container build kas/iot2050.yml:kas/opt/sm.yml
```
The full example and SWUpdate images already include SM support, so no extra
fragment is needed for those builds.

## Packages Provided

This layer declares the `IOT2050_META_SM_PACKAGES` variable in
`recipes-core/images/meta-sm-packages.inc`:
```
IOT2050_META_SM_PACKAGES ?= " \
		iot2050-proximity-driver \
		iot2050-eio-manager \
		iot2050-event-record \
		iot2050-conf-webui \
		iot2050-module-firmware-update \
		"
```
Image recipes will append this list to `IMAGE_INSTALL` only when
`IOT2050_SM_SUPPORT = "1"`.

## Device Tree Integration

This layer appends the SM-specific Device Tree Blob (DTB):
`ti/k3-am6548-iot2050-advanced-sm.dtb`

The bootloader logic automatically selects the correct DTB for the detected
board revision, so no separate `MACHINE` value is required. Downstream projects
needing to provide overrides should place `.bbappend` files in a
higher-priority layer.

## Related Documentation

- Composition & fragments: `doc/build-config.md`
- Architecture rationale: `doc/layer-architecture.md`
- Example layer (demos): `meta-example/README.md`

## Maintainers

See the top-level `MAINTAINERS` file in the repository root.

## License

MIT License – See `COPYING.MIT` in the repository root.