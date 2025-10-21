# Changelog

All notable changes to this project are documented here. Format loosely
follows Keep a Changelog; versions use SemVer (MAJOR.MINOR.PATCH).

Sections used per release:
- Added: new features / artifacts
- Changed: behavior or structural changes (backward compatible)
- Removed: removals requiring action
- Deprecated: discouraged items kept temporarily
- Security: key handling, signing, or update process changes
- Migration: explicit steps for adopters
- Internal: build / CI / maintenance notes (non-user visible)

See [CONTRIBUTING.md](CONTRIBUTING.md) for the detailed conventions.

## [Unreleased]
_Placeholder for next patch release (move entries here when ready)._ 

## [V01.06.01] - UNRELEASED
Refactor release introducing modular layer split, reproducible build
tooling, clearer composition UX, and comprehensive documentation overhaul.

### Added
- Modular feature / variant layers: `meta` `meta-node-red`, `meta-hailo`,
   `meta-sm` plus re-scoped `meta-example` (demo integration & feature
   flags include).
- Central feature toggle include:
   `meta-example/conf/include/iot2050-features.inc` defining
   `IOT2050_<FEATURE>_SUPPORT` flags.
- Aggregated package list includes per feature layer (e.g.
   `meta-node-red-packages.inc`, `meta-sm-packages.inc`, etc.) ensuring
   safe empty defaults via `??=`.
- Unified build configuration guide (`doc/build-config.md`) combining
   interactive menu + manual chaining, with ordering & reproducibility tips.
- Architecture & migration rationale: `doc/layer-architecture.md`.
- Fragment catalog for infrastructure / reproducibility / provisioning:
   `doc/fragment-catalog.md`.
- Operational docs: `doc/maintenance.md`, `doc/swupdate.md`,
   `doc/secure-boot.md`, `doc/qemu.md`, `doc/sdk.md` refreshed & linked.
- Images & Features matrix plus Profiles cheatsheet in `README.md`.
- SM / EIO support explicitly documented and implicitly bundled in
   example & SWUpdate descriptors.

### Changed
- Opt-in KAS fragments under `kas/opt/`: `example.yml`, `node-red.yml`,
   `sm.yml`, `hailo.yml`, `lxde.yml`, `docker.yml`, `secure-boot.yml`,
   `preempt-rt.yml`, `package-lock.yml`, `debian-mirror.yml`, `rpmb-setup.yml`,
   `upstream.yml`, provisioning fragments in `otpcmd/`, `sdk.yml`,
   emulation add-on `kas-iot2050-qemu.yml`.
- Image composition now uses feature flags (`IOT2050_<FEATURE>_SUPPORT`)
   in image recipes; layers publish packages but do not self-install.
- Node-RED, SM, Hailo, Example demos made first-class independent
   fragments when starting from minimal descriptor.
- Consolidated documentation into a single source of truth per topic
  (build-config, fragment-catalog, maintenance, swupdate, secure-boot).
- README simplified and reorganized: lifecycle flow.
- Improved quick start examples & ordering guidance for fragment chains.
- Refined secure boot docs to emphasize DEMO keys replacement and OTP
   provisioning ordering.
- QEMU descriptor now chainable to minimal path as well as example.
- Consistent 80-column soft wrap applied across all Markdown docs.

### Removed
- Legacy KAS fragments: `module.yml`, `no-node-red.yml`, `eio.yml`.
- Monolithic layer assumption; feature content moved to dedicated layers.
- Redundant / fragmented prior build workflow docs (superseded by
   `doc/build-config.md`).

### Security
- Clear warning and segregation of demonstration secure boot keys; docs
   add production replacement checklist.
- Provisioning fragments separated from signing to reduce accidental OTP
   programming during routine builds.
- Added reproducibility note to encourage APT snapshot locking for audit
   trails.

### Migration
1. Update `BBLAYERS` to add new layers (`meta`, `meta-example`,
    `meta-node-red`, `meta-hailo`, `meta-sm`).
2. Remove obsolete fragments (`module.yml`, `no-node-red.yml`, `eio.yml`).
3. Replace manual `IMAGE_INSTALL` injections (Node-RED/SM/Hailo/demos) with
    feature flags or appropriate fragments.
4. For minimal base parity with example image chain:
    `kas/iot2050.yml:kas/opt/example.yml:kas/opt/node-red.yml:kas/opt/sm.yml`.
5. Use `preempt-rt.yml` for RT kernel; pair with `package-lock.yml` +
    `debian-mirror.yml` if reproducibility required.
6. Secure boot: replace demo keys, add `secure-boot.yml` only after review;
    append a single `otpcmd/*` provisioning fragment when intentionally
    programming OTP.
7. Validate configuration:
    - `bitbake-layers show-layers`
    - `bitbake -e iot2050-image-example | grep IOT2050_.*_SUPPORT`
8. Update downstream documentation links if they pointed to old section
    numbers (anchor shims provided for common ones).

### Internal
- Introduced uniform package include pattern with `??=` empty defaults to
   prevent unresolved variable expansions.
- Adopted consistent markdown style (headings hierarchy, fenced code
   language hints, 80-col wrapping).
- CI adjustment accordingly.

[Unreleased]: https://github.com/siemens/meta-iot2050/compare/V01.05.01...HEAD
