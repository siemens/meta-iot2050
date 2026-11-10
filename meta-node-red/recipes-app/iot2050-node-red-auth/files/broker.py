#!/usr/bin/python3 -I
# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT
"""Local authentication only. Account writes use trusted root management paths."""

import base64
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import pwd
import socket
import stat
import struct
import subprocess
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backend import AuthError, Backend, MAX_REQUEST, ensure_directory


ADDRESS = Path("/run/iot2050-node-red-auth/auth.sock")


def peer_uid(connection):
    credentials = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    return struct.unpack("3i", credentials)[1]


class AuthenticationServer(HTTPServer):
    address_family = socket.AF_UNIX
    request_queue_size = 8

    def __init__(self, address, backend, editor_uids, http_uids):
        self.backend = backend
        self.editor_uids = editor_uids
        self.http_uids = http_uids
        # Four running jobs plus eight queued requests accommodate ordinary
        # parallel browser resource requests without an unbounded work queue.
        self.capacity = threading.BoundedSemaphore(12)
        self.workers = ThreadPoolExecutor(max_workers=4)
        self.address = address
        super().__init__(str(address), AuthenticationHandler)
        os.chmod(address, 0o600)

    def server_bind(self):
        self.socket.bind(self.server_address)
        self.server_name = "localhost"
        self.server_port = 0

    def get_request(self):
        connection, address = self.socket.accept()
        if peer_uid(connection) not in self.editor_uids | self.http_uids:
            connection.close()
            raise PermissionError("Authentication client is not permitted")
        connection.settimeout(10)
        return connection, address

    def process_request(self, request, client_address):
        if not self.capacity.acquire(blocking=False):
            request.close()
            return
        self.workers.submit(self.finish_client, request, client_address)

    def finish_client(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            # No request/body/password is included in this diagnostic.
            print("Node-RED authentication client failed", file=sys.stderr)
        finally:
            self.shutdown_request(request)
            self.capacity.release()

    def server_close(self):
        super().server_close()
        self.workers.shutdown(wait=True)
        self.address.unlink(missing_ok=True)


class AuthenticationHandler(BaseHTTPRequestHandler):
    server: AuthenticationServer

    def log_message(self, format, *args):
        pass  # Standard HTTP logs are not appropriate for credential requests.

    def reply(self, status, user=None):
        body = json.dumps({"user": user}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if status == 401:
            self.send_header("WWW-Authenticate", 'Basic realm="Node-RED", charset="UTF-8"')
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if peer_uid(self.connection) not in self.server.editor_uids:
            self.reply(403)
            return
        if self.path not in {"/editor/user", "/editor/authenticate"}:
            self.reply(404)
            return
        try:
            if (self.headers.get("Transfer-Encoding") or
                    self.headers.get("Content-Type") != "application/json"):
                raise ValueError("Invalid authentication request framing")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_REQUEST:
                raise ValueError("Invalid authentication request size")
            data = self.rfile.read(length)
            if len(data) != length:
                raise ValueError("Incomplete authentication request")
            request = json.loads(data)
            authenticate = self.path == "/editor/authenticate"
            fields = {"username", "password"} if authenticate else {"username"}
            if not isinstance(request, dict) or set(request) != fields:
                raise ValueError("Invalid authentication request fields")
            secret = request.get("password")
            # Only /editor/user may request the account-only lookup.
            if authenticate and secret is None:
                raise ValueError("Missing authentication password")
            user = self.server.backend.lookup(request["username"], secret)
        except (ValueError, AuthError):
            self.reply(401)
        except (OSError, subprocess.SubprocessError):
            self.reply(503)
        else:
            self.reply(200 if user else 401, user)

    def do_GET(self):
        if peer_uid(self.connection) not in self.server.http_uids:
            self.reply(403)
            return
        if self.path != "/http/authenticate":
            self.reply(404)
            return
        try:
            authorization = self.headers.get("Authorization", "")
            if len(authorization) > 2048:
                raise ValueError("Invalid credential length")
            scheme, value = authorization.split(" ", 1)
            if scheme.lower() != "basic":
                raise ValueError("Unsupported authentication scheme")
            decoded = base64.b64decode(value, validate=True).decode("utf-8")
            name, secret = decoded.split(":", 1)
            user = self.server.backend.lookup(name, secret, http=True)
        except (ValueError, AuthError):
            self.reply(401)
        except (OSError, subprocess.SubprocessError):
            self.reply(503)
        else:
            self.reply(200 if user else 401)


def client_uids(name):
    try:
        return {0, pwd.getpwnam(name).pw_uid}
    except KeyError:
        return {0}


def main():
    if os.getuid() != 0 or os.geteuid() != 0:
        raise AuthError("Authentication broker requires root")
    ensure_directory(ADDRESS.parent)
    if ADDRESS.exists():
        # systemd owns the singleton lifecycle. Do not follow or remove an
        # unexpected regular file/symlink at the privileged socket path.
        info = ADDRESS.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != 0:
            raise AuthError("Unsafe authentication socket")
        ADDRESS.unlink()
    with AuthenticationServer(ADDRESS, Backend(), client_uids("nodered"), client_uids("www-data")) as server:
        os.chmod(ADDRESS, 0o660)
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
