#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
# This is an example for recording wacthdog reset event.
#
import array
import fcntl
import os
import psutil
import time
from datetime import datetime
import grpc
from gRPC.EventInterface.iot2050_event_pb2 import (
    WriteRequest,
    ReadRequest
)
from gRPC.EventInterface.iot2050_event_pb2_grpc import EventRecordStub
from iot2050_event_global import iot2050_event_api_server


EVENT_STRINGS = {
    "wdt": "{} watchdog reset is detected"
}

WDTRESET_EVENT_TYPE = "IOT2050_EVENT.watchdog"

# Implement _IOR function for wdt kernel ioctl function
_IOC_NRBITS   =  8
_IOC_TYPEBITS =  8
_IOC_SIZEBITS = 14
_IOC_DIRBITS  =  2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT =(_IOC_NRSHIFT+_IOC_NRBITS)
_IOC_SIZESHIFT =(_IOC_TYPESHIFT+_IOC_TYPEBITS)
_IOC_DIRSHIFT  =(_IOC_SIZESHIFT+_IOC_SIZEBITS)

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2
def _IOC(direction,type,nr,size):
    return (((direction)  << _IOC_DIRSHIFT) |
        ((type) << _IOC_TYPESHIFT) |
        ((nr)   << _IOC_NRSHIFT) |
        ((size) << _IOC_SIZESHIFT))
def _IOR(type, number, size):
    return _IOC(_IOC_READ, type, number, size)

WDIOC_GETBOOTSTATUS = _IOR(ord('W'), 2, 4)
WDIOF_CARDRESET = 0x20
WDT_PATH = "/dev/watchdog"

def write_event(event_type, event):
    with grpc.insecure_channel(iot2050_event_api_server) as channel:
        stub = EventRecordStub(channel)
        response = stub.Write(WriteRequest(event_type=event_type, event=event))

def read_event(event_type):
    with grpc.insecure_channel(iot2050_event_api_server) as channel:
        stub = EventRecordStub(channel)
        response = stub.Read(ReadRequest(event_type=event_type))
    return response.event

def feeding_the_watchdog(fd):
    while True:
       ret = os.write(fd, b'watchdog')
       print("Feeding the watchdog ...")
       time.sleep(30)

def record_wdt_events():
    status = array.array('h', [0])
    fd = os.open(WDT_PATH, os.O_RDWR)
    if fcntl.ioctl(fd, WDIOC_GETBOOTSTATUS, status, 1) < 0:
        print("Failed to get wdt boot status!")

    if (WDIOF_CARDRESET & status[0]):
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        wdt_event = EVENT_STRINGS["wdt"].format(boot_time)
        existed_events = read_event(WDTRESET_EVENT_TYPE)
        if not wdt_event in existed_events:
            write_event(WDTRESET_EVENT_TYPE, wdt_event)

    feeding_the_watchdog(fd)

    os.close(fd)

if __name__ == "__main__":
    record_wdt_events()
