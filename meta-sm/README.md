# meta-sm – IoT2050 SM Variant Layer

_Applies to meta-iot2050 v1.6.0+ modular layout._  

This layer supplies the optional SM (Sensor / Extended IO) variant
user-space components and device tree for boards equipped with the
additional peripherals.

## 1. Overview

`meta-sm` is additive: it does NOT redefine a separate machine by default.
Instead, the canonical Example and SWUpdate image descriptors include its
content implicitly. When using the minimal base descriptor you opt in via the
`sm.yml` fragment (`IOT2050_SM_SUPPORT=1`).

## 2. Scope & Purpose

| Category | Scope |
|----------|-------|
| Sensors & IO mgmt | EIO manager, proximity / event utilities |
| Variant services | Event recording, configuration web UI integration |
| Firmware helper  | Module firmware update helper (signal module) |
| Device tree      | SM-specific DTB addition(s) |

Excluded: Secure boot logic, key provisioning, general demo apps (see
`meta-example`).

## 3. Feature Flag & Fragment

Enabled by either:
```
# Minimal path + SM
./kas-container build kas/iot2050.yml:kas/opt/sm.yml

# Or in local.conf
IOT2050_SM_SUPPORT = "1"
```
The full example & SWUpdate images already include SM support—no fragment is
needed there.

## 4. Packages Provided

Declared in `meta-sm/recipes-core/images/meta-sm-packages.inc`:
```
IOT2050_META_SM_PACKAGES ?= " \
		iot2050-proximity-driver \
		iot2050-eio-manager \
		iot2050-event-record \
		iot2050-conf-webui \
		iot2050-module-firmware-update \
		"
```
Image recipes append this list only when `IOT2050_SM_SUPPORT = "1"`.

| Package | Purpose |
|---------|---------|
| iot2050-proximity-driver | Sensor / proximity input support |
| iot2050-eio-manager | External IO management daemon (GPIO/services) |
| iot2050-event-record | Lightweight event / condition logging |
| iot2050-conf-webui | Integration endpoints for configuration UI |
| iot2050-module-firmware-update | Signal module firmware update helper |

> There are no packagegroups here; prior references to `packagegroup-meta-sm*`
> were removed in the refactor—this README reflects the current model.

## 5. Device Tree Integration

The layer appends the SM-specific DTB(s):
```
ti/k3-am6548-iot2050-advanced-sm.dtb
```
Selection occurs via bootloader logic choosing the correct DTB for the board
revision (no separate MACHINE value required). Downstreams needing overrides
should place bbappend files in a higher-priority layer.

## 6. Usage Examples

Minimal base + SM only (quick footprint comparison):
```
./kas-container build kas/iot2050.yml:kas/opt/sm.yml
```

Full example image (already includes SM):
```
./kas-container build kas-iot2050-example.yml
```

Add SM late to an existing minimal + demos chain:
```
./kas-container build \
	kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml
```

## 7. Customization Guidance

Downstreams adding new SM‑related services should:
1. Create a new recipe under a separate layer (avoid patching this layer if
	 possible).
2. Append its package name to a new feature list variable guarded by a flag
	 (mirroring the existing pattern) or extend `IOT2050_META_SM_PACKAGES` in a
	 bbappend.
3. Keep services disabled-by-default unless hardware presence is guaranteed.

## 8. Production Notes

- Remove unused SM services if deploying on non-SM hardware (omit fragment or
	unset flag).
- Review any exposed web endpoints (conf web UI) for authentication hardening
	in product images.
- Pair with reproducibility fragments (`package-lock.yml`) for audit builds.

## 9. Related Documentation

- Composition & fragments: `doc/build-config.md`
- Architecture rationale: `doc/layer-architecture.md`
- Secure boot & provisioning: `doc/secure-boot.md`
- Example layer (demos): `meta-example/README.md`

## 10.  Maintainers

See top-level `MAINTAINERS` file in the repository root.

## 11. License

MIT License – See `COPYING.MIT` (repository root).