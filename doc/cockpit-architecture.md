# IOT2050 Cockpit Integration Architecture

This document defines the architecture and extension rules for IOT2050-specific
Cockpit integrations. It is intentionally smaller and more stable than the
feature-specific documentation. New Cockpit pages and integrations should
follow these boundaries unless a design change is explicitly documented.

## Goals

The IOT2050 Cockpit integration should:

- keep each feature independently installable and reviewable;
- use Cockpit's standard package and manifest model;
- keep privileged operations behind a small, fixed backend boundary;
- avoid adding unnecessary public HTTP or nginx APIs;
- provide a consistent navigation, theme, error, and task experience;
- allow new hardware and application integrations without merging unrelated
  frontends or backends into one package.

## Current integration map

The current self-developed integrations are separate Cockpit packages:

| Feature | Layer and package | Cockpit ID | Navigation | Availability | Backend boundary |
| --- | --- | --- | --- | --- | --- |
| Firmware | `meta-example`, `iot2050-cockpit-firmware` | `iot2050-firmware` | System | Example and SWUpdate images | `iot2050-fwmgr` and its systemd task workers |
| EIO Config | `meta-sm`, `iot2050-cockpit-eio-config` | `iot2050-eio-config` | System | SM board condition | EIO configuration bridge on the loopback interface |
| Device Admin | `meta-example`, `iot2050-cockpit-device-admin` | `iot2050-device-admin` | System | Example and SWUpdate images | Fixed-operation `iot2050-device-admin` helper |

The corresponding implementation and feature documentation are:

- [Firmware Center](firmware-center.md)
- [Device Admin](iot2050-device-admin.md)
- [EIO Config Cockpit README](../meta-sm/recipes-app/iot2050-cockpit-eio-config/README.md)

The current navigation is intentionally flat within Cockpit's standard
sections:

```text
System
├── Firmware
├── EIO Config       (SM only)
└── Device Admin
```

All IOT2050 Cockpit pages use the `System` menu section. Use explicit `order`
values to keep related IOT2050 entries together. Do not introduce a custom
sidebar category or a new top-level section unless the number of IOT2050
entries grows substantially and the navigation cost justifies it.

## Package and identity rules

Every integration has four identities that must be considered separately:

1. Debian/Isar package name;
2. Cockpit package directory under `/usr/share/cockpit/`;
3. manifest `name`;
4. user-visible menu label.

The package name, Cockpit directory, and manifest `name` should be stable once
the feature is released. The menu label may be improved independently, but a
rename must update the manifest, page title, documentation, image installation,
and all references together.

Use a feature-specific name for new packages, for example:

```text
iot2050-cockpit-<feature>
iot2050-cockpit-<feature>-integration
```

Do not use a generic package name such as `iot2050-system-webui` for unrelated
features. Do not reuse a Cockpit ID for a different feature.

## Backend and privilege boundaries

A Cockpit page is not a general root shell. Every privileged operation must use
a deliberately limited backend interface.

### Read-only operations

Read-only status and inspection may use an existing authenticated Cockpit
API, a fixed local client, or a narrowly scoped loopback service. The interface
must still validate requests and avoid arbitrary paths or commands.

### Hardware-changing operations

Operations that write hardware or device configuration must use a dedicated
manager or fixed-operation service boundary:

```text
Cockpit page
    -> authenticated Cockpit client
    -> fixed local client or root-only Unix socket
    -> fwmgr/provider
    -> hardware or system service
```

Examples:

- Firmware uses fwmgr and its persistent task model.
- EIO Config uses its existing configuration bridge.
- Device Admin uses fixed certificate-installation operations.
- The Web Gateway exposes the optional image-bundled OSS Clearing archive
  through the fixed `/oss` URL. The URL is available only when the archive is
  supplied as a build input.

Do not add a new public nginx route merely to connect a Cockpit page to a
privileged operation. Do not pass arbitrary command names, filesystem paths, or
service names from the browser to a root helper.

## Feature integration contract

Each new Cockpit feature should provide the following:

- a dedicated recipe and package boundary;
- a manifest with a unique `name`, clear label, keywords, and explicit
  availability conditions where needed;
- a page directory with local static assets and a clear entrypoint;
- a fixed backend boundary for privileged operations;
- a short feature document describing user-visible behavior and operational
  requirements;
- image integration only in the image variants that support the feature.

SM-specific features must not be installed or shown on non-SM images. Use
manifest conditions and backend capability checks as separate safeguards; a
frontend-only condition is not a sufficient security boundary.

## Change management

When an integration needs to violate one of these rules, document the reason
and the resulting security, packaging, navigation, and maintenance impact in
its design or feature documentation before implementation.
