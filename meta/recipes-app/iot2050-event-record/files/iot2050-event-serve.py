#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#   Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
from concurrent import futures
import datetime
import grpc
from iot2050_event import (
    write_event,
    read_event,
    EventIOError
)
from iot2050_event_global import (
    EVENT_API_SERVER_HOSTNAME,
    EVENT_API_SERVER_PORT
)
from gRPC.EventInterface.iot2050_event_pb2 import (
    WriteRequest, WriteReply,
    ReadRequest, ReadReply
)
from gRPC.EventInterface.iot2050_event_pb2_grpc import (
    EventRecordServicer,
    add_EventRecordServicer_to_server
)


class EventRecordServicer(EventRecordServicer):

    def Write(self, request: WriteRequest, context):
        try:
            write_event(request.event_type, request.event)
        except EventIOError as e:
            return WriteReply(status=1, message=f'{e}')

        return WriteReply(status=0, message='OK')

    def Read(self, request: ReadRequest, context):
        event = read_event(request.event_type)

        return ReadReply(status=0, message='OK', event=event)


def serve():
    iot2050_event_api_server = "{}:{}".format(
        EVENT_API_SERVER_HOSTNAME, EVENT_API_SERVER_PORT)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    add_EventRecordServicer_to_server(
        EventRecordServicer(), server
    )
    server.add_insecure_port(iot2050_event_api_server)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
