#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
from concurrent import futures
import datetime
import grpc
from gRPC.EIOManager.iot2050_eio_pb2 import (
    DeployRequest, DeployReply,
    RetrieveRequest, RetrieveReply,
    SyncTimeRequest, SyncTimeReply,
    UpdateFirmwareRequest, UpdateFirmwareReply,
    CheckFWURequest, CheckFWUReply,
    ReadEIOEventRequest, ReadEIOEventReply
)
from gRPC.EIOManager.iot2050_eio_pb2_grpc import (
    EIOManagerServicer as BaseEIOManagerServicer,
    add_EIOManagerServicer_to_server
)
from iot2050_eio_global import (
    iot2050_eio_api_server,
    EIO_FS_TIMESTAMP,
)


class EIOManagerServicer(BaseEIOManagerServicer):

    def Deploy(self, request: DeployRequest, context):
        return DeployReply(status=0, message='OK')

    def Retrieve(self, request: RetrieveRequest, context):
        return RetrieveReply(status=0,
                             message='OK',
                             yaml_data='')

    def SyncTime(self, request: SyncTimeRequest, context):
        if request.HasField("time"):
            time = request.time
        else:
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(EIO_FS_TIMESTAMP, 'w', encoding='ascii') as f:
            f.write(time)

        return SyncTimeReply(status=0, message=f'{time}')

    def UpdateFirmware(self, request: UpdateFirmwareRequest, context):
        return UpdateFirmwareReply(status=0, message='OK')

    def CheckFWU(self, request: CheckFWURequest, context):
        return CheckFWUReply(status=0, message='OK')

    def ReadEIOEvent(self, request: ReadEIOEventRequest, context):
        return ReadEIOEventReply(status=0, message='OK', event='')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    add_EIOManagerServicer_to_server(EIOManagerServicer(), server)
    server.add_insecure_port(iot2050_eio_api_server)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
