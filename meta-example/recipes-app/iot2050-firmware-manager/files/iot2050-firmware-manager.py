#!/usr/bin/env python3
# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""Unix socket daemon for the IOT2050 firmware manager."""

import os
import signal
import socket
import socketserver
import threading

from iot2050_firmware_manager import (
    FirmwareManager,
    ManagerError,
    ProviderRegistry,
    decode_request,
    encode_response,
)


class FirmwareRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        for raw_line in self.rfile:
            try:
                request = decode_request(raw_line.decode("utf-8"))
                response = self.server.manager.handle(request)
            except ManagerError as error:
                response = {
                    "v": 1,
                    "id": None,
                    "ok": False,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                    },
                }
            self.wfile.write(encode_response(response).encode("utf-8"))


class FirmwareServer(socketserver.UnixStreamServer):
    def __init__(self, socket_path, manager):
        self.manager = manager
        super().__init__(socket_path, FirmwareRequestHandler, bind_and_activate=False)
        self.socket.close()
        self.socket = socket.socket(fileno=3)


def activated_socket_fd():
    try:
        listen_pid = int(os.environ["LISTEN_PID"])
        listen_fds = int(os.environ["LISTEN_FDS"])
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("Firmware manager requires systemd socket activation") from error
    if listen_pid != os.getpid() or listen_fds != 1:
        raise RuntimeError("Expected exactly one systemd-activated socket")
    return 3


def main():
    activated_socket_fd()
    registry = ProviderRegistry()
    registry.discover()
    manager = FirmwareManager(registry)
    with FirmwareServer(None, manager) as server:
        def stop_server(signum, frame):
            manager.task_runner.stop_accepting()
            threading.Thread(target=server.shutdown, daemon=True).start()

        signal.signal(signal.SIGTERM, stop_server)
        signal.signal(signal.SIGINT, stop_server)
        server.serve_forever()
        manager.task_runner.shutdown()


if __name__ == "__main__":
    main()
