# IOT2050 Event Record

IOT2050 Event Record is using for reading and recording events, such as
power up, power loss, tilted, uncovered, watchdog reset and eio events.

The core is a RPC service implemented with the help of gPRC.

## Event record services

The `iot2050-event-record.service` and `iot2050-event-serve.service` are systemd
services, they could be managed by `systemctl`. The `iot2050-event-record`
collects events from various source then consume the API exposed by `iot2050-event-serve`
to wrap the collected events as `IOT2050-EventRecord` events and save them to
syslog. Then these wrapped events could be read by `journalctl` or by gRPC APIs.

## Predefined events

### Power events and Extended IO(EIO) events

Power events and EIO events are injected to `journal(syslog)` by default.

To check them on IOT2050:

```sh
root@iot2050-debian:~# journalctl SYSLOG_IDENTIFIER=IOT2050-EventRecord
Oct 23 22:36:12 iot2050-debian IOT2050-EventRecord[323]: IOT2050_EVENTS.power: 2023-10-23 22:36:00 the device is powered up
Oct 23 22:40:21 iot2050-debian IOT2050-EventRecord[323]: IOT2050_EVENTS.power: 2023-10-23 22:34:4 [2] power loss
Oct 23 22:40:21 iot2050-debian IOT2050-EventRecord[323]: IOT2050_EVENTS.eio: 2023-10-23 22:12:54 [11] slot1 lost
```

### Sensor events

Only the IOT2050-SM hardware variant contains the tilt / uncover sensor.
For all other variants these sensor events are not available, so they are 
disabled by default. If you are using an SM variant you may enable the
sensor (tilted and uncovered) event recording. To enable them on an SM
device, create a systemd drop-in for iot2050-event-record.service as
follows:

```sh
mkdir -p /etc/systemd/system/iot2050-event-record.service.d/
cp /usr/lib/iot2050/event/iot2050-event-record.conf /etc/systemd/system/iot2050-event-record.service.d/
systemctl daemon-reload
systemctl restart iot2050-event-record.service
```
If changing the tilting threshold and uncovering threshold is expected, please
refer to the ``iot2050-event-record.conf`` for the details.

### Watchdog events

If watchdog event recording is expected, please refer to [WATCHDOG.md](./WATCHDOG.md).

## Development

### How to inject a new event?

First, please link the `EventInterface` to the customized application.
```sh
# In IOT DUT
ln -s /usr/lib/iot2050/event/gRPC/EventInterface /path/to/customized-app/gRPC/EventInterface

# In Source code
ln -s recipes-app/iot2050-event-record/files/gRPC/EventInterface /path/to/customized-app/gRPC/EventInterface
```

Then, use the `Write` and `Read` functions to communicate with
`iot2050-event-serve.service`, as follows:

```python
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

### Regenerate the gRPC python modules if proto file changed

If the `proto` file needs to be changed when customizing a new application
to inject event, please update the gRPC in the original path as follows.

```sh
python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. gRPC/EventInterface/iot2050-event.proto
```
