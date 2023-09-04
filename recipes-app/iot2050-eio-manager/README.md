# IOT2050 Extended IO Subsystem

The IOT2050 Extended IO (EIO) subsystem is for managing the extended
IOs, currently the PLC1200 signal modules.

This subsystem is only valid on IOT2050-SM variant at the moment.

The core is a RPC service implemented with the help of gPRC.

In addition:
 - A FUSE service for loading the eio file system.
 - A time syncing service for sync the system time to extended IO
   controller.
 - A cli tool for communicating with the gRPC server:
   - Deploy/Retrieve extended IO configurations
   - Update firmware for the extended IO controller or modules.
 - A firmware updating monitoring service for notify updating while
   firmware does not match.

## Regenerate the gRPC python modules if proto file changes:

```shell
python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. gRPC/EIOManager/iot2050-eio.proto
```

## Local debugging

When debug locally, create a `files/.env` file to store the local environments.

An example:

```python
# IOT2050 Extended IO API server hostname
EIO_API_SERVER_HOSTNAME="localhost"

# IOT2050 Extended IO API server port
EIO_API_SERVER_PORT="5020"

# Periodically syncing timestamp to Extended IO controller
EIO_TIME_SYNC_INTERVAL=30

# Extended IO FUSE filesystem path for timestamp syncing
EIO_FS_TIMESTAMP="/tmp/eiofs-proc-datetime"

# Extended IO FUSE filesystem path for configuration
EIO_FS_CONTROL="/tmp/eiofs-controller-control"
EIO_FS_CONFIG="/tmp/eiofs-controller-config"

# JSON schema files for validating the config yaml
EIO_SCHEMA_ROOT="${PWD}/config-schema"

# template file for yaml config
EIO_CONFIG_TEMP_ROOT="${PWD}/config-template"

EIO_FWU_META="${PWD}/bin/firmware-version"

EIO_FS_FW_VER="/tmp/eiofs-proc-version"

EIO_FWU_MAP3_FW_BIN="${PWD}/bin/map3-fw.bin"
```

Then under `files` folder, run:

```shell
python3 iot2050-eio-service.py
```

to start the service. If you want to run the cli, use:

```shell
python3 iot2050-eio-cli.py
```
