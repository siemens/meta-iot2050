# IOT2050 Event Record

IOT2050 Event Record is using for reading and recording events, such as
power up, power loss, tilted, uncovered, watchdog reset and eio events.

The core is a RPC service implemented with the help of gPRC.

In addition:
- A event-serve service for writing and reading syslog.
- A event-record service for recording events.

# Sensor events

In default, the sensor events, i.e. tilted and uncovered events, are disabled.
If enabling logging of sensor events is expected, please create a systemd
drop-in for `iot2050-event-record.service`, as follows:

```sh
cp /usr/lib/iot2050/event/iot2050-event-record.conf /etc/systemd/system/iot2050-event-record.service.d/
```

# Watchdog events example

If watchdog events recording is expected, please run the following commands,
or write a new one referring to this example.
```sh
python3 /usr/lib/iot2050/event/iot2050-event-wdt.py
```

## How to record a new event?

First, please link the `EventInterface` to the customized application.
```sh
# In IOT DUT
ln -s /usr/lib/iot2050/event/gRPC/EventInterface /path/to/customized-app/gRPC/EventInterface

# In Source code
ln -s recipes-app/iot2050-event-record/files/gRPC/EventInterface /path/to/customized-app/gRPC/EventInterface
```

Then, use the `Write` and `Read` functions to communicate with
`iot2050-event-serve.service`, as follows:

```py
import grpc
from gRPC.EventInterface.iot2050_event_pb2 import (
    WriteRequest,
    ReadRequest
)
from gRPC.EventInterface.iot2050_event_pb2_grpc import EventRecordStub


def write_event(event_type, event):
    with grpc.insecure_channel(iot2050_event_api_server) as channel:
        stub = EventRecordStub(channel)
        response = stub.Write(WriteRequest(event_type=event_type, event=event))

    if response.status:
        print(f'Event Record writes event result: {response.status}')
        print(f'Event Record writes event message: {response.message}')

def read_event(event_type):
    with grpc.insecure_channel(iot2050_event_api_server) as channel:
        stub = EventRecordStub(channel)
        response = stub.Read(ReadRequest(event_type=event_type))
    return response.event
```

And, please find the api definition in `gRPC/EventInterface/iot2050-event.proto`.

## Regenerate the gRPC python modules if proto file changes:

```sh
python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. gRPC/EventInterface/iot2050-event.proto
```
