# Building and Using the SDK

> TL;DR: Build with `:kas/opt/sdk.yml`, find the `iot2050-image-example-sdk-iot2050-debian-iot2050.tar.xz`
> artifact, and follow the `README.sdk` inside the extracted tarball.

## Host Machine Support
The cross-compilation SDK currently supports only Linux x86-64 host machines.

## Building the SDK
You can build the SDK by chaining the `sdk.yml` fragment to an image build
or by selecting the SDK option in the interactive KAS menu.

**Build Command**:
```sh
./kas-container build kas-iot2050-example.yml:kas/opt/sdk.yml
```

**Interactive Menu**:
```sh
./kas-container menu
```
Then, select the "Build SDK" option.

## Artifacts
After the build completes, the SDK is available in two forms in the
`build/tmp/deploy/images/iot2050/` directory:

1.  **SDK Tarball**:
    `iot2050-image-example-sdk-iot2050-debian-iot2050.tar.xz`

2.  **Docker Image Archive**:
    `sdk-iot2050-debian-arm64-docker-archive.tar.xz`

## Installation and Usage

### Tarball
For installation and usage instructions, please extract the SDK tarball and
follow the guidance in the `README.sdk` file contained within it.

### Docker
To import the SDK into a Docker host, run the following command:
```sh
docker load -i build/tmp/deploy/images/iot2050/sdk-iot2050-debian-arm64-docker-archive.tar.xz
```
