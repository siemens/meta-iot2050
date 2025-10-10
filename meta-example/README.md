# meta-example – IoT2050 Demo / Example Layer

_Applies to meta-iot2050 v1.6.0+ (modular layer architecture)._ See the
top-level `README.md` and `doc/layer-architecture.md` for the broader
architectural rationale.

## Overview

`meta-example` provides demonstration and showcase content, helper tools, and
integration glue used by the canonical Example images
(`kas-iot2050-example.yml` and its SWUpdate variant). It focuses on
discoverability and fast hardware bring-up rather than a production-minimal
footprint.

## Scope & Purpose

| Category | Purpose |
|----------|---------|
| Demo applications | Illustrate IO, networking, and service configuration. |
| Example implementations | Provide a reference integration for downstream layers. |
| Development helpers | Include convenience utilities (debug, scripting). |
| Web interface components | Offer configuration and monitoring front-ends. |
| Serial & board tools | Supply mode switching, board info, and setup helpers. |

## Included Components (Illustrative)

The image recipe (`iot2050-image-example.bb`) pulls in a curated, evolving set
of packages via feature flags (see below).

| Functional Area | Examples (non-exhaustive – consult recipe for current list) |
|------------------|------------------------------------------------------------|
| GPIO / EIO | EIO manager, GPIO tools |
| Web UI | Configuration / dashboard interface |
| Serial utilities | RS232/RS485 mode tools |
| Monitoring | Basic system and service status helpers |
| Developer aids | Selected Python / Node.js tools (trimmed for size) |

> The exact package list may change. Rely on feature flags and KAS fragments
> instead of hard-coding package names in downstream projects.

## Feature Flags Integration

`conf/include/iot2050-features.inc` centralizes soft switches consumed by image
recipes. Relevant to this layer:
```
# (Excerpt – see file for full list and defaults)
IOT2050_NODE_RED_SUPPORT ?= "0"
IOT2050_SM_SUPPORT       ?= "0"
IOT2050_HAILO_SUPPORT    ?= "0"
```

The example image descriptors (non-minimal) set these flags to enable bundled
content. When starting from the minimal base descriptor, you must add the
optional fragments instead:
```sh
./kas-container build \
	kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml
```

## How to Use This Layer

**Fast path** (already includes this layer + demos, Node-RED, SM):
```sh
./kas-container build kas-iot2050-example.yml
```

**SWUpdate A/B variant** (dual rootfs + .swu output):
```sh
./kas-container build kas-iot2050-swupdate.yml
```

**From a lean minimal base**, opt-in only to this layer’s demos:
```sh
./kas-container build kas/iot2050.yml:kas/opt/example.yml
```

**Add Node-RED & SM** (achieves feature parity with the full example path):
```sh
./kas-container build \
	kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml
```

## Customization & Extensibility

Two common paths exist: start broad to explore, or start lean for control.

**Path A: Fast evaluation**
1. Build the reference Example image: `kas-iot2050-example.yml`. This
   includes this layer, Node-RED, SM, and other helper tooling.
2. Optionally, test A/B updates with `kas-iot2050-swupdate.yml`.
3. Make a list of what you actually used and need for your product.

**Path B: Controlled minimal start**
1. Build the minimal base image: `kas/iot2050.yml`.
2. Add only the required optional fragments (e.g., `example.yml` for demos,
   plus `node-red.yml`, `sm.yml`, etc.).
3. Create a downstream layer (e.g., `meta-yourprod`) with an image recipe
   that derives from the minimal one.
4. Introduce feature flags following the established pattern and collect them
   in an include file.
5. From there, do what you need—prune demos and add reproducibility or
   security fragments only when they become relevant.

## Security & Production Note
This layer is for demonstration purposes. Before productization:
- Replace any demo certificates or keys.
- Remove unneeded developer utilities introduced by this layer.
- Rebuild with reproducibility fragments (`package-lock.yml`, optional
  `debian-mirror.yml`) for audit trails.

## Related Documentation

- Top-level composition & fragments: `doc/build-config.md`
- Layer architecture & migration: `doc/layer-architecture.md`
- SWUpdate flow: `doc/swupdate.md`

## Maintainers

See the top-level `MAINTAINERS` file in the repository root.

## License

MIT License – See `COPYING.MIT` in the repository root.