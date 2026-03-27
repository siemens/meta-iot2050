This README describes the optional credential payload expected under this
`files/` directory for the `trust-center-credential` recipe.

The recipe expects the following files with these exact names:

- `keystore`
  Client credential store used by the signing workflow. This is commonly a
  `.p12` file.
- `truststore`
  Trust store used to validate the remote signing service. This is commonly a
  `.jks` file.
- `trust-center-mpk.crt`
  Public certificate for the primary signing key, in PEM format.
- `trust-center-smpk.crt`
  Public certificate for the secondary signing key, in PEM format.
- `worker.env`
  Environment file used by the signing client helper.

Expected `worker.env` content
-----------------------------

The `worker.env` file should use standard shell-style `NAME=VALUE` entries.
See `worker.env.example` for the expected format.

The currently used variables are:

- `TC_HOST`
  Hostname of the signing service.
- `TC_PORT`
  Port of the signing service.
- `TC_WORKER`
  Signing worker or signer identifier.
- `TC_KEYSTORE_PASSWD`
  Password for `keystore`.
- `TC_TRUSTSTORE_PASSWD`
  Password for `truststore`.

How this directory is used
--------------------------

These files are not meant to be provided by this repository. They are expected
to be prepared by the build environment, for example by:

- a CI pipeline
- a local developer setup
- a downstream product integration

This keeps the recipe reusable while allowing each build environment to provide
its own certificates, credential stores, and connection settings.

Important notes
---------------

- The file names must remain unchanged unless the recipe is updated as well.
- Treat all credential files and passwords as sensitive material.
- Do not commit real credentials or environment secrets to the repository.
