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

The example image descriptors set these flags through KAS fragments. See the
[build configuration guide](../doc/build-config.md) for composition details.

## How to Use This Layer

Build the full example image, which includes this layer, Node-RED, and SM:

```sh
./kas-container build kas-iot2050-example.yml
```

To add only this layer's demos to the minimal image:

```sh
./kas-container build kas/iot2050.yml:kas/opt/example.yml
```

## Customization & Extensibility

For product images, start from the minimal image, add only the required
fragments, and maintain the resulting image recipe in a downstream layer.

## Security & Production Note

This layer is for demonstration purposes. Before productization:

- Follow the [demo signing key policy](../doc/build-config.md#demo-signing-keys).
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