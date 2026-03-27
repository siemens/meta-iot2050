This README describes the optional `tc-signclient/` source payload placed under
this `files/` directory for the `trust-center-remote-signer` recipe.

The recipe expects a source tree named `tc-signclient/` under this directory
and imports it via `file://tc-signclient`.

Expected layout
---------------

At build time, this directory should look like:

- `tc-signclient/`
	Local copy of the sign-client source tree
- `tc-signclient/bin/`
	Client launcher scripts or executables
- `tc-signclient/lib/`
	Runtime libraries or bundled JAR files
- `tc-signclient/conf/`
	Configuration files required by the client

Why the source is provided locally
----------------------------------

The sign-client sources are not kept in this repository. They are expected to
be copied here by one of the following methods:

- CI injects the required source tree before the build starts
- a developer copies a local test tree into this directory
- a downstream layer or product build prepares its own sign-client payload

This keeps the recipe flexible and allows each build environment to provide the
sign-client implementation it needs.
