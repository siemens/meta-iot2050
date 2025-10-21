#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
import grpc
import time
from gRPC.EIOManager.iot2050_eio_pb2 import SyncTimeRequest
from gRPC.EIOManager.iot2050_eio_pb2_grpc import EIOManagerStub
from iot2050_eio_global import (
    iot2050_eio_api_server,
    EIO_TIME_SYNC_INTERVAL
)


def run():
    print(f"Start syncing Extended IO timestamp every {EIO_TIME_SYNC_INTERVAL} seconds.")
    while True:
        with grpc.insecure_channel(iot2050_eio_api_server) as channel:
            stub = EIOManagerStub(channel)
            response = stub.SyncTime(SyncTimeRequest())
        print(f"Extended IO timestamp syncing result: {response.status}")
        print(f"Extended IO timestamp synced to: {response.message}")
        time.sleep(EIO_TIME_SYNC_INTERVAL)


if __name__ == "__main__":
    run()
