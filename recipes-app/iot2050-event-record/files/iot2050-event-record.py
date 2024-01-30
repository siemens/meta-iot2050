#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
import os
import sys
import psutil
import threading
import time
from datetime import datetime
from systemd import journal
from enum import Enum
import grpc
from gRPC.EventInterface.iot2050_event_pb2 import (
    WriteRequest,
    ReadRequest
)
from gRPC.EventInterface.iot2050_event_pb2_grpc import EventRecordStub
from gRPC.EIOManager.iot2050_eio_pb2_grpc import EIOManagerStub
from gRPC.EIOManager.iot2050_eio_pb2 import (
    ReadEIOEventRequest
)
from iot2050_event_global import (
    iot2050_event_api_server,
    iot2050_eio_api_server
)

EVENT_TYPES = {
    "power": "IOT2050_EVENTS.power",
    "tilt": "IOT2050_EVENTS.tilted",
    "uncover": "IOT2050_EVENTS.uncovered",
    "eio": "IOT2050_EVENTS.eio",
}
EVENT_STRINGS = {
    "power": "{} the device is powered up",
    "tilt": "{} the device is tilted",
    "uncover": "{} the device is uncovered",
    "common": "{}"
}


TIMEOUT_SEC = 15
def grpc_server_on(channel) -> bool:
    try:
        grpc.channel_ready_future(channel).result(timeout=TIMEOUT_SEC)
        return True
    except grpc.FutureTimeoutError:
        return False

def is_grpc_servers_ready():
    with grpc.insecure_channel(iot2050_event_api_server) as channel:
        if not grpc_server_on(channel):
            print(f"ipv4:{iot2050_event_api_server}: Failed to connect to remote host: Connection refused")
            return False

    return True

def is_eiod_servers_existed():
    with grpc.insecure_channel(iot2050_eio_api_server) as channel:
        if not grpc_server_on(channel):
            return False

    return True

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

error_messages = []
def read_eio_event():
    with grpc.insecure_channel(iot2050_eio_api_server) as channel:
        stub = EIOManagerStub(channel)
        response = stub.ReadEIOEvent(ReadEIOEventRequest())

    # Only print the error info once to avoid interference
    if response.status and not response.message in error_messages:
        error_messages.append(response.message)
        print(f'Event Record reads eio event result: {response.status}')
        print(f'Event Record reads eio event message: {response.message}')

    return response.event

def record_power_events(has_eio=False):
    try:
        existed_events = read_event(EVENT_TYPES["power"])
        # power up
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        power_up_event = EVENT_STRINGS["power"].format(boot_time)
        if not power_up_event in existed_events:
            write_event(EVENT_TYPES["power"], power_up_event)

        # power loss, which is recorded by eio
        if has_eio:
            for event in read_eio_event().splitlines():
                if not "power loss" in event or \
                    event in existed_events:
                        continue
                write_event(EVENT_TYPES["power"], event)
    except Exception as e:
        print(e)

def record_eio_events():
    '''Record all eio events, not including power up and power loss events'''
    while True:
        existed_events = read_event(EVENT_TYPES["eio"])
        for event in read_eio_event().splitlines():
            if "power" in event or \
                event in existed_events:
                    continue
            write_event(EVENT_TYPES["eio"], event)
        time.sleep(5)



IIO_IMU_PATH = "/sys/devices/platform/bus@100000/2030000.i2c/i2c-5/5-006a/"
IIO_PRO_PATH = "/sys/devices/platform/bus@100000/2030000.i2c/i2c-5/5-0044/"
ACCEL_CRITICAL_VALUE = 1000
LUX_CRITICAL_VALUE = 300
def record_sensor_events():
    accel_x_raw = "{}/in_accel_x_raw"
    accel_y_raw = "{}/in_accel_y_raw"
    accel_z_raw = "{}/in_accel_z_raw"
    pro_raw = "{}/in_proximity0_raw"
    imu_w = os.walk(IIO_IMU_PATH)
    pro_w = os.walk(IIO_PRO_PATH)
    for (dirpath, dirnames, filenames) in imu_w:
        if "in_accel_x_raw" in filenames:
            accel_x_raw = accel_x_raw.format(dirpath)
            accel_y_raw = accel_y_raw.format(dirpath)
            accel_z_raw = accel_z_raw.format(dirpath)
            break
    for (dirpath, dirnames, filenames) in pro_w:
        if "in_proximity0_raw" in filenames:
            pro_raw = pro_raw.format(dirpath)
            break
    with open(accel_x_raw, 'r') as x, \
        open(accel_y_raw, 'r') as y, \
        open(accel_z_raw, 'r') as z, \
        open(pro_raw, 'r') as l:
        is_uncovered = False
        while True:
            # Detect tilt sensor event
            x.seek(0)
            y.seek(0)
            z.seek(0)
            old_x = int(x.read())
            old_y = int(y.read())
            old_z = int(z.read())

            time.sleep(0.3)

            x.seek(0)
            y.seek(0)
            z.seek(0)
            if abs(int(x.read()) - old_x) > ACCEL_CRITICAL_VALUE or \
                abs(int(y.read()) - old_y) > ACCEL_CRITICAL_VALUE or \
                abs(int(z.read()) - old_z) > ACCEL_CRITICAL_VALUE:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tilted_event = EVENT_STRINGS["tilt"].format(now)
                write_event(EVENT_TYPES["tilt"], tilted_event)

            # Detect tamper sensor event
            l.seek(0)
            lux = int(l.read())
            if lux < LUX_CRITICAL_VALUE and not is_uncovered:
                is_uncovered = True
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                uncover_event = EVENT_STRINGS["uncover"].format(now)
                write_event(EVENT_TYPES["uncover"], uncover_event)
            elif lux > LUX_CRITICAL_VALUE and is_uncovered:
                is_uncovered = False

def event_record():
    if not is_grpc_servers_ready():
        sys.exit(1)
    to_record_eio_events = is_eiod_servers_existed()

    # Record the power events
    record_power_events(has_eio=to_record_eio_events)

    to_record_sensor_events = os.getenv('RECORD_SENSOR_EVENTS')
    # Record the tilt/tamper sensor events
    if to_record_sensor_events:
        sensor_thread = threading.Thread(target=record_sensor_events)
        sensor_thread.start()

    # Record the eio event
    if to_record_eio_events:
        eio_thread = threading.Thread(target=record_eio_events)
        eio_thread.start()

    if to_record_sensor_events:
        sensor_thread.join()
    if to_record_eio_events:
        eio_thread.join()


if __name__ == "__main__":
    event_record()
