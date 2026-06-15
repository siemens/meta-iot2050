#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023-2026
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
from concurrent import futures
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
import threading
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
from iot2050_eio_config import (
    deploy_config,
    retrieve_config,
    ConfigError,
)
from iot2050_eio_global import (
    iot2050_eio_api_server,
    iot2050_eio_webui_api_server,
    EIO_FS_TIMESTAMP,
)
from iot2050_eio_fwu import (
    update_firmware,
    FirmwareUpdateChecker
)
from iot2050_eio_event import read_eio_event


BRIDGE_CONFIG_PATH = '/api/v1/eio/config'


def make_bridge_response(ok, code, message, data=None):
    return {
        'ok': ok,
        'code': code,
        'message': message,
        'data': data or {},
    }


class EIOManagerServicer(BaseEIOManagerServicer):

    def Deploy(self, request: DeployRequest, context):
        status, _, message = deploy_yaml_config(request.yaml_data)
        return DeployReply(status=status, message=message)

    def Retrieve(self, request: RetrieveRequest, context):
        status, _, message, yaml_data = retrieve_yaml_config()
        return RetrieveReply(status=status,
                             message=message,
                             yaml_data=yaml_data)

    def SyncTime(self, request: SyncTimeRequest, context):
        if request.HasField("time"):
            time = request.time
        else:
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(EIO_FS_TIMESTAMP, 'w', encoding='ascii') as f:
            f.write(time)

        return SyncTimeReply(status=0, message=f'{time}')

    def UpdateFirmware(self, request: UpdateFirmwareRequest, context):
        status, message = update_firmware(request.firmware, request.entity)
        return UpdateFirmwareReply(status=status, message=f'{message}')

    def CheckFWU(self, request: CheckFWURequest, context):
        status, message = FirmwareUpdateChecker().collect_fwu_info()
        return CheckFWUReply(status=status, message=message)

    def ReadEIOEvent(self, request: ReadEIOEventRequest, context):
        try:
            event = read_eio_event()
        except Exception as e:
            return ReadEIOEventReply(status=1, message=f'{e}', event=f'')

        return ReadEIOEventReply(status=0, message='OK', event=event)


def deploy_yaml_config(yaml_data):
    try:
        deploy_config(yaml_data)
    except ConfigError as e:
        return 1, 'CONFIG_ERROR', f'{e}'

    return 0, 'OK', 'OK'


def retrieve_yaml_config():
    try:
        yaml_data = retrieve_config()
    except ConfigError as e:
        return 1, 'CONFIG_ERROR', f'{e}', ''

    return 0, 'OK', 'OK', yaml_data


class EIOWebUIBridgeHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != BRIDGE_CONFIG_PATH:
            self._send_json(404, make_bridge_response(
                False,
                'NOT_FOUND',
                f'Unsupported API path: {self.path}'
            ))
            return

        status, code, message, yaml_data = retrieve_yaml_config()
        http_status = 200 if status == 0 else 422
        self._send_json(http_status, make_bridge_response(
            status == 0,
            code,
            'Configuration retrieved successfully.' if status == 0 else message,
            {'yaml_data': yaml_data}
        ))

    def do_PUT(self):
        if self.path != BRIDGE_CONFIG_PATH:
            self._send_json(404, make_bridge_response(
                False,
                'NOT_FOUND',
                f'Unsupported API path: {self.path}'
            ))
            return

        try:
            content_length = int(self.headers.get('Content-Length', '0'))
            raw_body = self.rfile.read(content_length).decode('utf-8')
            request_body = json.loads(raw_body) if raw_body else {}
            yaml_data = request_body['yaml_data']
            if not isinstance(yaml_data, str):
                raise TypeError('yaml_data must be a string')
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._send_json(400, make_bridge_response(
                False,
                'INVALID_JSON',
                f'Invalid JSON body: {e}'
            ))
            return
        except KeyError:
            self._send_json(400, make_bridge_response(
                False,
                'MISSING_YAML_DATA',
                'Request body must include yaml_data.'
            ))
            return
        except (TypeError, ValueError) as e:
            self._send_json(400, make_bridge_response(
                False,
                'INVALID_YAML_DATA',
                f'Invalid yaml_data value: {e}'
            ))
            return

        status, code, message = deploy_yaml_config(yaml_data)
        http_status = 200 if status == 0 else 422
        self._send_json(http_status, make_bridge_response(
            status == 0,
            code,
            'Configuration deployed successfully.' if status == 0 else message
        ))

    def do_POST(self):
        self._send_json(405, make_bridge_response(
            False,
            'METHOD_NOT_ALLOWED',
            'Use PUT /api/v1/eio/config to deploy configuration.'
        ))

    def do_DELETE(self):
        self._send_json(405, make_bridge_response(
            False,
            'METHOD_NOT_ALLOWED',
            'DELETE is not supported for this resource.'
        ))

    def do_PATCH(self):
        self._send_json(405, make_bridge_response(
            False,
            'METHOD_NOT_ALLOWED',
            'PATCH is not supported for this resource.'
        ))

    def do_HEAD(self):
        self.send_response(405)
        self.send_header('Allow', 'GET, PUT')
        self.end_headers()

    def log_message(self, format, *args):
        return

    def _send_json(self, http_status, payload):
        encoded = json.dumps(payload).encode('utf-8')
        self.send_response(http_status)
        self.send_header('Allow', 'GET, PUT')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def serve_webui_bridge():
    host, port = iot2050_eio_webui_api_server.rsplit(':', 1)
    http_server = ThreadingHTTPServer((host, int(port)), EIOWebUIBridgeHandler)
    thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    thread.start()
    return http_server

def serve():
    try:
        serve_webui_bridge()
    except (OSError, ValueError) as e:
        # Keep the existing gRPC/CLI API available even if the optional
        # Cockpit WebUI bridge cannot bind its loopback HTTP port.
        print(f'Warning: EIO WebUI bridge disabled: {e}', file=sys.stderr)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    add_EIOManagerServicer_to_server(EIOManagerServicer(), server)
    server.add_insecure_port(iot2050_eio_api_server)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
