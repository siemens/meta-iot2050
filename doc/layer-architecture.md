# IoT2050 Layer Architecture
_Applies to version: v1.6.0+_

> TL;DR: Layers are now strictly modular. Core BSP lives in `meta/`,
> optional features (Node-RED, Hailo, SM variant) each have their own
> layer, and image recipes gate inclusion via
> `IOT2050_<FEATURE>_SUPPORT` flags plus KAS opt fragments.

---

## 1. Goals of the Refactor

The layer restructuring addresses these objectives:

1. Clear separation of concerns (BSP vs feature vs board/variant vs
   optional accelerators)
2. Modular opt‑in features (Node-RED, Hailo, SM variant) with minimal
   cross-layer coupling
3. Predictable image composition via small KAS opt fragments instead of
   monolithic toggles
4. Easier long-term maintenance and review (smaller diffs per layer,
   narrower OWNERSHIP)
5. Explicit feature gating in image recipes while keeping feature layers
   “dumb” (data only)
6. Backward-compatible migration path for downstream users (simple BBLAYERS
   + flag updates)

## 2. High-level Structure

```
	+---------------------------------------------------------+
	|                      Final Images                       |
	+---------------------------------------------------------+
				^ (composed by image recipes)
				|
	+---------------+-----------------------------------------+
	|        Optional Feature / Variant Layers                |
	|  (opt-in; additive; removable without breaking core)    |
	|                                                         |
	|  +-------------+  +-------------+  +-------------+      |
	|  | meta-node-  |  |  meta-hailo |  |   meta-sm   |      |
	|  |   red       |  | (Hailo AI)  |  | (SM variant)|      |
	|  | (Node-RED)  |  +-------------+  +-------------+      |
	|  +-------------+                                         |
	|  +---------------------------------------------------+  |
	|  | meta-example (demo / example images / feature flags)| |
	|  +---------------------------------------------------+  |
	+---------------------------^-----------------------------+
						|
						| (all depend on core)
						v
					+----------------------+
					|        meta          |
					|  Core BSP (boot,     |
					|  kernel, firmware,   |
					|  base enablement)    |
					+----------------------+
```

Notes:
- meta provides only what is required to boot and update the platform.
- Feature / variant layers add strictly additive content; removal does not
	break core builds.
- The example layer (meta-example) serves as a reference integration rather
	than a dumping ground.

> Implicit vs Selectable: The canonical full Example and SWUpdate image
> descriptors already include demo content (example.yml), Node-RED and SM
> variant fragments. These components are exposed as independent toggles
> only when the “Example image (minimal HW enablement)” variant is selected
> (Kconfig limits prompts with `depends on IMAGE_BASE`). This lets
> downstreams build up a tailored example-like stack from a lean starting
> point while keeping the out‑of‑box experience unchanged for the full
> example / SWUpdate images.

## 3. Layer Responsibilities

### 3.1 Core BSP: meta/
Scope: U-Boot, TF-A, OP-TEE, kernel, firmware blobs, minimal / minimal
images. Contains new meta/recipes-core/images/meta-packages.inc
aggregating common base meta packages.

### 3.2 Example & Demo: meta-example/
Scope: Demonstration applications and the canonical example images
(iot2050-image-example.bb, SWUpdate variant, feature toggles include file).
Provides conf/include/iot2050-features.inc centralizing soft feature flags
(all default to disabled). Carries helper meta packages for bundling
optional app sets.

### 3.3 Node-RED Feature: meta-node-red/
Scope: Node-RED core plus curated pre-installed nodes and industrial
protocol plugins. Layer conf/layer.conf force-loads
meta-node-red-packages.inc (defines IOT2050_META_NODE_RED_PACKAGES). Image
recipes decide (via flags) whether to append those packages.

### 3.4 Hailo AI Accelerator: meta-hailo/
Scope: Hailo firmware, runtime, kernel integration and any tuning
fragments. Pattern: meta-hailo-packages.inc publishes
IOT2050_META_HAILO_PACKAGES (default empty if feature disabled elsewhere).

### 3.5 SM Variant / Extended Modules: meta-sm/
Scope: SM (Security Module / sensor & extended IO) variant support:
configuration web UI, EIO manager, event recording, proximity / sensor
drivers, variant DTBs. Provides meta-sm-packages.inc for aggregated
packages and SM-specific DTB list extension. Sensor/event features
disabled by default because only SM hardware ships these peripherals.

## 4. Feature Toggle Strategy

Central definitions live in:
meta-example/conf/include/iot2050-features.inc

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

Flags use ?= (early visible defaults). Aggregated package lists use ??= so a
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

## 5. KAS Fragment Usage (opt-in Build Composition)

Optional KAS fragments (kas/opt/):

- example.yml: Pulls in meta-example layer and builds example image set.
- node-red.yml: Enables Node-RED flag and adds meta-node-red layer.
- hailo.yml: Enables Hailo support and adds meta-hailo layer.
- sm.yml: Enables SM variant packages / sensors / EIOs.

Example combined build:
```
./kas-container build kas-iot2050-example.yml:kas/opt/hailo.yml
```

## 6. Migration Guide

1. Update BBLAYERS: remove legacy monolithic layer, add individual layers:
	```
	BBLAYERS += " \
	  ${TOPDIR}/../meta-iot2050/meta \
	  ${TOPDIR}/../meta-iot2050/meta-example \
	  ${TOPDIR}/../meta-iot2050/meta-node-red \
	  ${TOPDIR}/../meta-iot2050/meta-hailo \
	  ${TOPDIR}/../meta-iot2050/meta-sm \
	"
	```
	etc.) with new fragments listed above.
2. Replace now-removed KAS opt fragments (`module.yml`, `no-node-red.yml`,
   `eio.yml`) with the new granular fragments listed above.
3. If you previously forced Node-RED packages in IMAGE_INSTALL, remove
   them and set:
	```
	IOT2050_NODE_RED_SUPPORT = "1"
	```
	Or include kas/opt/node-red.yml.
4. For Hailo support add meta-hailo and enable the flag if image logic
   requires it.
5. For SM sensor/event features:
	```
	IOT2050_SM_SUPPORT = "1"
	```
	Then enable specific service drop-ins per meta-sm README.
6. Remove direct references to now internal aggregate variables
   (IOT2050_META_PACKAGES) unless intentionally relied upon; prefer
   feature-specific lists.

## 7. Design Decisions & Conventions

- Layer granularity: Split by feature domain (smaller review scope,
	optional inclusion).
- Feature gating location: Image recipe (clear build intent; layers
	declarative).
- Variable naming: `IOT2050_<FEATURE>_SUPPORT` flags (consistent,
	grep-friendly).
- Defaults: Disabled ("0") to keep minimal base builds.
- Aggregated packages: Publish via `*_PACKAGES` vars to avoid repetition.
- Inclusion mechanism: `require` in layer.conf for package list `.inc`
	ensures symbols exist.
- Empty safety: Provide `??=` empty definitions to prevent unresolved
	expansions.

## 8. SM Variant Sensors Note

Only the SM hardware variant exposes the related sensor set (proximity,
tilt, uncover). Disabled by default to avoid dangling services on non-SM
devices. Enable via:
```
IOT2050_SM_SUPPORT = "1"
```
Then follow meta-sm guidance for per-service activation.

## 9. Example BBLayers & Local Config Snippet

```
BBLAYERS ?= " \
  ${TOPDIR}/../meta-iot2050/meta \
  ${TOPDIR}/../meta-iot2050/meta-example \
  ${TOPDIR}/../meta-iot2050/meta-node-red \
  ${TOPDIR}/../meta-iot2050/meta-hailo \
  ${TOPDIR}/../meta-iot2050/meta-sm \
"
```

Enable Node-RED & SM in `local.conf` without KAS fragments:
```
IOT2050_NODE_RED_SUPPORT = "1"
IOT2050_SM_SUPPORT = "1"
```

## 10. Glossary

- **BSP**: Board Support Package: bootloader, kernel, device trees, firmware.
- **Feature Layer**: Self-contained functional add-on (e.g. Node-RED).
- **Variant Layer**: Hardware variant specifics / extra peripherals (SM).
- **KAS Fragment**: YAML include enabling a subset of layers, flags, or build options.

## 3. Image Variants
Ordered by typical usage prominence:
1. Example image – full feature showcase
2. Example image (SWUpdate A/B)
3. Example image (minimal HW enablement) – lean starting point

### 3.1 Implicit vs Selectable Content
Full example and SWUpdate images implicitly include Node-RED, SM, and
example demo content. The minimal hardware enablement variant keeps these
optional so you can incrementally add:
- Example demos (`kas/opt/example.yml`)
- Node-RED (`kas/opt/node-red.yml`)
- SM variant (`kas/opt/sm.yml`)

> Implicit vs Selectable: These components surface as independent toggles
> only when the “Example image (minimal HW enablement)” variant is chosen
> (Kconfig limits prompts with `depends on IMAGE_BASE`). This lets
> downstreams build a tailored stack from a lean starting point while the
> out‑of‑box full example / SWUpdate experience remains unchanged.


