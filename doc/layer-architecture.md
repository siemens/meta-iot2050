# IoT2050 Layer Architecture
_Applies to version: v1.6.0+_

> TL;DR: Layers are now strictly modular. Core BSP lives in `meta/`, optional
> features (Node-RED, Hailo, SM variant) each have their own layer, and image
> recipes gate inclusion via `IOT2050_<FEATURE>_SUPPORT` flags plus KAS opt
> fragments.

---

## Architectural Goals

The layer architecture is designed to achieve these objectives:

1.  **Clear Separation of Concerns**: Distinguishes between the core Board
    Support Package (BSP), optional features, hardware variants, and
    accelerators.
2.  **Modularity**: Enables features like Node-RED and Hailo AI as optional,
    opt-in modules with minimal cross-layer dependencies.
3.  **Predictable Composition**: Uses small, single-purpose KAS fragments for
    image assembly instead of complex, monolithic toggles.
4.  **Maintainability**: Simplifies long-term maintenance and code review by
    keeping layers focused and diffs small.
5.  **Explicit Gating**: Centralizes feature enablement within image recipes,
    while allowing layers to remain simple data providers.

## High-level Structure

```
+---------------------------------------------------------+
|        Final Images (Example, SDK, SWUpdate, ...)       |
+---------------------------------------------------------+
                           ^
                           | (composed from)
                           |
+---------------------------------------------------------+
| meta-example (Demo Recipes, Feature Flags, Integration) |
+---------------------------------------------------------+
                           ^
                           | (builds on)
                           |
+--------------------------+------------------------------+
|                          |                              |
|   Optional Feature Layers|         Core BSP Layer       |
|  (additive, opt-in)      |                              |
|                          |                              |
| +----------------------+ |                              |
| |    meta-node-red     | |                              |
| +----------------------+ |         +--------------+     |
| |      meta-hailo      | |-------->|     meta     |     |
| +----------------------+ |         +--------------+     |
| |       meta-sm        | |                              |
| +----------------------+ |                              |
|                          |                              |
+--------------------------+------------------------------+
```

Notes:
- `meta` provides only what is required to boot and update the platform.
- Feature / variant layers add strictly additive content; removal does not
  break core builds.
- The example layer (`meta-example`) serves as a reference integration rather
  than a dumping ground.

> Implicit vs Selectable: The canonical full Example and SWUpdate image
> descriptors already include demo content (example.yml), Node-RED and SM
> variant fragments. These components are exposed as independent toggles
> only when the “Example image (minimal HW enablement)” variant is selected
> (Kconfig limits prompts with `depends on IMAGE_BASE`). This lets
> downstreams build up a tailored example-like stack from a lean starting
> point while keeping the out‑of‑box experience unchanged for the full
> example / SWUpdate images.

## Layer Responsibilities

### Core BSP: meta/
Scope: U-Boot, TF-A, OP-TEE, kernel, firmware blobs, minimal images.
Contains new `meta/recipes-core/images/meta-packages.inc` aggregating
common base meta packages.

> For more details, see the [Core BSP README](../meta/README.md).

### Example & Demo: meta-example/
Scope: Demonstration applications and the canonical example images
(`iot2050-image-example.bb`, SWUpdate variant, feature toggles include file).
Provides `conf/include/iot2050-features.inc` centralizing soft feature flags
(all default to disabled). Carries helper meta packages for bundling
optional app sets.

> For more details, see the [Example Layer README](../meta-example/README.md).

### Node-RED Feature: meta-node-red/
Scope: Node-RED core plus curated pre-installed nodes and industrial
protocol plugins. Layer `conf/layer.conf` force-loads
`meta-node-red-packages.inc` (defines `IOT2050_META_NODE_RED_PACKAGES`). Image
recipes decide (via flags) whether to append those packages.

> For more details, see the [Node-RED Layer README](../meta-node-red/README.md).

### Hailo AI Accelerator: meta-hailo/
Scope: Hailo firmware, runtime, kernel integration and any tuning
fragments. Pattern: `meta-hailo-packages.inc` publishes
`IOT2050_META_HAILO_PACKAGES` (default empty if feature disabled elsewhere).

> For more details, see the [Hailo AI Layer README](../meta-hailo/README.md).

### SM Variant / Extended Modules: meta-sm/
Scope: SM variant support: configuration web UI, EIO manager, event recording,
proximity / sensor drivers, variant DTBs. Provides `meta-sm-packages.inc` for
aggregated packages and SM-specific DTB list extension.

> For more details, see the [SM Variant Layer README](../meta-sm/README.md).

## Feature Toggle Strategy

Central definitions live in:
`meta-example/conf/include/iot2050-features.inc`

```
IOT2050_NODE_RED_SUPPORT ?= "0"
IOT2050_HAILO_SUPPORT    ?= "0"
IOT2050_SM_SUPPORT       ?= "0"
... (other flags) ...

# Safe empty defaults (ensures IMAGE_INSTALL expansions never reference
# undefined symbols)
IOT2050_META_NODE_RED_PACKAGES ??= ""
IOT2050_META_HAILO_PACKAGES    ??= ""
IOT2050_META_SM_PACKAGES       ??= ""
```

Why both `?=` and `??=`?

Flags use `?=` (early visible defaults). Aggregated package lists use `??=` so a
providing layer may set them earlier (or override with stronger assignment)
before the final lazy fallback to empty.

Image recipe pattern (simplified example):
```
IMAGE_INSTALL += " \
    ${@ '${IOT2050_META_NODE_RED_PACKAGES}' if d.getVar('IOT2050_NODE_RED_SUPPORT') == '1' else ''} \
    ${@ '${IOT2050_META_SM_PACKAGES}' if d.getVar('IOT2050_SM_SUPPORT') == '1' else ''} \
    ${@ '${IOT2050_META_HAILO_PACKAGES}' if d.getVar('IOT2050_HAILO_SUPPORT') == '1' else ''} \
    "
```

Rationale: gating stays local to the image (layer isolation). Layers only
publish what could be installed, never whether to install.

## KAS Fragment Usage (opt-in Build Composition)

Optional KAS fragments (`kas/opt/`):

- `example.yml`: Pulls in `meta-example` layer and builds example image set.
- `node-red.yml`: Enables Node-RED flag and adds `meta-node-red` layer.
- `hailo.yml`: Enables Hailo support and adds `meta-hailo` layer.
- `sm.yml`: Enables SM variant packages / sensors / EIOs.

Example combined build:
```
./kas-container build kas-iot2050-example.yml:kas/opt/hailo.yml
```

## Downstream Customization

This project uses the KAS build tool to manage configuration layers and
features. Customization should primarily be done by creating or extending KAS
configuration files.

### How KAS Manages Layers

You do **not** need to manually edit `bblayers.conf`. The KAS configuration
files (`.yml`) handle this for you.

When a KAS fragment is included in a build, it instructs KAS which layers to
add to the configuration. For example, `kas/opt/example.yml` contains:

```yaml
repos:
  meta-iot2050:
    layers:
      meta-example:
```

This automatically adds the `meta-hailo` layer to the build's `BBLAYERS`
variable.

### Enabling Features

There are two primary methods for enabling features:

**1. Chaining KAS Fragments (Recommended)**

The most robust method is to chain optional KAS fragments (`kas/opt/*.yml`)
to a base descriptor. Each fragment is responsible for adding its required
layer and setting the corresponding `SUPPORT` flag.

For example, to add Node-RED and SM variant support to the base image, you
would run:

```
./kas-container build kas/iot2050.yml:kas/opt/node-red.yml:kas/opt/sm.yml
```

This is the preferred method for CI and reproducible builds, as the entire
configuration is self-contained in the command.

**2. Using `local.conf` (Local Development)**

For quick tests, you can enable features directly in your `conf/local.conf`
file by setting the `SUPPORT` flags. This method assumes the required layers
are already part of your KAS configuration (e.g., included in the base
`.yml` file but not activated).

```
# In conf/local.conf
IOT2050_NODE_RED_SUPPORT = "1"
IOT2050_SM_SUPPORT = "1"
```

This approach is useful for debugging but is less portable.

### Example: Building a Feature-Rich Image

You can combine multiple fragments to create a tailored image. For instance,
to build the example image and add Hailo support:

```
./kas-container build kas-iot2050-example.yml:kas/opt/hailo.yml
```

Refer to the `kas/opt/` directory for a full list of available fragments.

## Design Decisions & Conventions

-   **Layer granularity**: Split by feature domain (smaller review scope,
    optional inclusion).
-   **Feature gating location**: Image recipe (clear build intent; layers
    declarative).
-   **Variable naming**: `IOT2050_<FEATURE>_SUPPORT` flags (consistent,
    grep-friendly).
-   **Defaults**: Disabled ("0") to keep minimal base builds.
-   **Aggregated packages**: Publish via `*_PACKAGES` vars to avoid repetition.
-   **Inclusion mechanism**: `require` in `layer.conf` for package list `.inc`
    ensures symbols exist.
-   **Empty safety**: Provide `??=` empty definitions to prevent unresolved
    expansions.

## Glossary

-   **BSP**: Board Support Package: bootloader, kernel, device trees, firmware.
-   **Feature Layer**: Self-contained functional add-on (e.g. Node-RED).
-   **Variant Layer**: Hardware variant specifics / extra peripherals (SM).
-   **KAS Fragment**: YAML include enabling a subset of layers, flags, or build
    options.
