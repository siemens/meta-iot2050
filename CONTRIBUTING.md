# Contributing

We welcome contributions in several forms, e.g.

* Sponsoring
* Documenting
* Testing
* Coding
* etc.

Please read [14 Ways to Contribute to Open Source without Being a Programming Genius or a Rock Star](https://web.archive.org/web/20200919165912/https://smartbear.com/blog/test-and-monitor/14-ways-to-contribute-to-open-source-without-being/?feed=test-monitor).

Please check issue page and look for unassigned ones or create a new one.

Working together in an open and welcoming environment is the foundation of our
success, so please respect our [Code of Conduct](CODE_OF_CONDUCT.md).

## Guidelines

### Workflow

We use the
[Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)
and review all changes we merge to master.

We appreciate any contributions, so please use the [Forking Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow)
and send us `Merge Requests`. 

### Patch files generation

Some components may use git patch files to add functionality or fix bugs, such
as linux kernel or u-boot. Please use the command below to generate such patches:

```shell
git format-patch --abbrev=12 --no-numbered --zero-commit --no-signature ...
```

## Recipe Maintenance and Versioning Guidelines

This repository follows the Yocto Project’s conventions for recipe versioning.
For comprehensive details on PV (recipe version) and PR (recipe revision),
contributors should consult the official Yocto documentation:

- [Yocto Reference Manual: Variables](https://docs.yoctoproject.org/ref-manual/variables.html)
- [Yocto Development Manual: Packages](https://docs.yoctoproject.org/dev-manual/packages.html)

### Repository-specific conventions

In addition to the Yocto standards, please observe the following rules when
contributing to this repository:

- **PR (recipe revision) starts at `1`** (not `r0`).
- **PV (recipe version) for all in-repo packages must follow
  [Semantic Versioning 2.0](https://semver.org/)**.

By adhering to these guidelines, we ensure consistency and compatibility across
all contributions. Thank you for helping maintain high standards in this project.

## Changelog Conventions

This project keeps a human-readable `CHANGELOG.md` using a structure loosely
based on Keep a Changelog plus additional sections (Security, Migration,
Internal). Follow these rules when contributing changes:

1. Always update `CHANGELOG.md` in the same commit (or series) that introduces
    user-visible changes (features, deprecations, removals, security updates,
    migration requirements, documentation restructuring).
2. Use present tense and imperative mood (e.g. "Add fragment for...", "Deprecate
    variable ...") for new entries.
3. Categorize under one (or more if justified) of the standard headings:
    - Added / Changed / Removed / Deprecated / Security / Migration / Internal.
4. Avoid duplicate subsections: consolidate multiple bullet points under one
    heading rather than creating additional repeated headings.
5. For unreleased work target the `[Unreleased]` section. When preparing a patch
    release (e.g. 1.6.1) create an empty placeholder section:
    `## [1.x.y] - UNRELEASED` directly below `[Unreleased]` so PRs can move
    entries there once scope is defined.
6. Do NOT retroactively edit released sections except to correct typos or add
    missing security disclosures (note corrections in a new bullet if impactful).
7. Link additions (new docs) should briefly state purpose, not just filename.
8. Migration bullets must be actionable (commands, flags, fragment chains) and
    avoid ambiguous phrasing.
9. Security section only for items affecting boot chain integrity, signing,
     encryption, update verification, or vulnerability remediation.
10. Comparison links must be updated for each release.
11. Trivial typo-only doc fixes may omit changelog entry.

Example bullet formatting:
```
### Added
- Add `preempt-rt.yml` fragment providing low-latency kernel option.
```

If a PR only changes internal CI or test infrastructure, prefer the Internal
section. Small typo-only doc fixes may omit changelog if truly trivial.

Release Process (summary):
1. Ensure `[Unreleased]` is empty (move items to new version block).
2. Add comparison link references at bottom for the new tag.
3. Replace `UNRELEASED` with the release date (UTC) in ISO format.
4. Tag the release and push.
5. Immediately add a new placeholder section for the next patch/minor.

This keeps downstream consumers informed and lowers migration friction.

## Developer's Certificate of Origin 1.1

In order to pass the checks, commit with signoff option

```shell
git commit --signoff
```

When signing-off a patch for this project like this

    Signed-off-by: Random J Developer <random@developer.example.org>

using your real name (no pseudonyms or anonymous contributions), you declare the
following:

    By making a contribution to this project, I certify that:

        (a) The contribution was created in whole or in part by me and I
            have the right to submit it under the open source license
            indicated in the file; or

        (b) The contribution is based upon previous work that, to the best
            of my knowledge, is covered under an appropriate open source
            license and I have the right under that license to submit that
            work with modifications, whether created in whole or in part
            by me, under the same open source license (unless I am
            permitted to submit under a different license), as indicated
            in the file; or

        (c) The contribution was provided directly to me by some other
            person who certified (a), (b) or (c) and I have not modified
            it.

        (d) I understand and agree that this project and the contribution
            are public and that a record of the contribution (including all
            personal information I submit with it, including my sign-off) is
            maintained indefinitely and may be redistributed consistent with
            this project or the open source license(s) involved.

