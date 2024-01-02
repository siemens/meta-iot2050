# IOT2050 Extended IO Subsystem

The IOT2050 Extended IO (EIO) subsystem is for managing the extended
IOs, currently the PLC1200 signal modules.

This subsystem is only valid on IOT2050-SM variant at the moment.

The core is a RPC service implemented with the help of gPRC.

In addition:
 - A FUSE service for loading the eio file system.

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
```

Then under `files` folder, run:

```shell
python3 iot2050-eio-service.py
```

to start the service.
