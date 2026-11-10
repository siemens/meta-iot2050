# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT
"""Lightweight activation controller; configuration files are the only state."""

import datetime
from contextlib import contextmanager
import errno
import fcntl
import http.client
import os
from pathlib import Path
import pwd
import re
import secrets
import socket
import ssl
import stat
import subprocess
import time
from typing import Iterator

from backend import AuthError, Backend, atomic_write, command, ensure_directory, secure_file, username


CONFIG = Path("/etc/node-red")
SETTINGS = CONFIG / "settings.js"
SECRET = CONFIG / "credential-secret"
GATEWAY = Path("/run/iot2050-node-red/gateway.conf")
LEGACY_GATEWAY = Path("/etc/nginx/conf.d/iot2050-node-red.conf")
TEMPLATE = Path("/usr/share/iot2050/node-red-control/nginx.conf")
GATEWAY_MARKER = "# Managed by iot2050-node-red-control\n"
GATEWAY_PORT = 1880
GATEWAY_APPLY_TIMEOUT = 10
MARKER = "// Managed by iot2050-node-red-control\n"
SETTINGS_TEXT = MARKER + """'use strict';
module.exports = {
    uiHost: '127.0.0.1',
    uiPort: 1881,
    httpAdminRoot: '/admin',
    httpNodeRoot: '/http',
    adminAuth: require('/usr/lib/iot2050/node-red-auth/admin-auth.js'),
    credentialSecret: require('node:fs').readFileSync('/etc/node-red/credential-secret', 'utf8').trim(),
    functionExternalModules: false,
    externalModules: {
        autoInstall: false,
        palette: { allowInstall: false, allowUpload: false },
        modules: { allowInstall: false }
    },
    editorTheme: { projects: { enabled: false } },
    logging: { console: { level: 'info', metrics: false, audit: true } }
};
"""


@contextmanager
def locked() -> Iterator[None]:
    ensure_directory(CONFIG)
    fd = os.open(CONFIG / ".control-lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise AuthError("Unsafe Node-RED control lock")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def checked(arguments: list[str]) -> None:
    result = command(arguments)
    if result.returncode:
        raise AuthError("Node-RED system operation failed")


def systemctl(*arguments: str) -> None:
    result = subprocess.run(["/usr/bin/systemctl", *arguments], capture_output=True,
                             text=True, check=False, timeout=180, close_fds=True,
                            env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LC_ALL": "C"})
    if result.returncode:
        raise AuthError("Node-RED service operation failed")


def configured() -> bool:
    if not SETTINGS.exists():
        return False
    secure_file(SETTINGS)
    if SETTINGS.read_text() != SETTINGS_TEXT:
        raise AuthError("Unexpected Node-RED settings; manual review is required")
    check_secret()
    return True


def check_secret() -> None:
    secure_file(SECRET)
    if stat.S_IMODE(SECRET.stat().st_mode) != 0o640:
        raise AuthError("Unsafe Node-RED credential secret permissions")
    if not re.fullmatch(r"[0-9a-f]{64}", SECRET.read_text().strip()):
        raise AuthError("Invalid Node-RED credential secret")


def prepare_secret(gid: int) -> None:
    if not SECRET.exists():
        atomic_write(SECRET, secrets.token_hex(32) + "\n", 0o640, gid=gid)
        return
    check_secret()
    if SECRET.stat().st_gid != gid:
        # Repair a secret published before the old setup completed its chown.
        os.chown(SECRET, 0, gid)


def service_state() -> dict[str, str]:
    result = command(["/usr/bin/systemctl", "show", "node-red.service",
                      "--property=ActiveState,SubState,Result,UnitFileState"])
    properties = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    if result.returncode or not properties.get("ActiveState"):
        raise AuthError("Cannot read Node-RED service state")
    return properties


def configuration_health() -> tuple[bool, str | None]:
    try:
        return configured(), None
    except AuthError as error:
        return False, str(error)
    except (OSError, UnicodeError):
        return False, "Cannot read Node-RED configuration"


def account_health(actor: str) -> tuple[bool, str | None]:
    backend = Backend()
    try:
        if not (backend.state / "users.json").exists():
            return False, None
        with backend.locked():
            return actor in backend.users(), None
    except AuthError as error:
        return False, str(error)
    except (OSError, ValueError):
        return False, "Cannot read Node-RED account configuration"


def status(actor: str) -> dict[str, object]:
    properties = service_state()
    active_state = properties["ActiveState"]
    has_configuration, configuration_error = configuration_health()
    account_exists, account_error = account_health(actor)
    return {
        "installed": Path("/usr/bin/node-red").exists(), "actor": actor,
        "configured": has_configuration, "configuration_error": configuration_error,
        "account_error": account_error, "running": active_state == "active",
        "active_state": active_state, "sub_state": properties.get("SubState", ""),
        "result": properties.get("Result", ""),
        "autostart": properties.get("UnitFileState") == "enabled",
        "gateway": active_state == "active" and gateway_ready(),
        "admin_path": "/admin/", "http_path": "/http/",
        "account_exists": account_exists,
    }


def certificate_check() -> None:
    cert = Path("/etc/iot2050/web-gateway/tls.crt")
    key = Path("/etc/iot2050/web-gateway/tls.key")
    secure_file(cert)
    secure_file(key)
    if key.stat().st_mode & 0o077:
        raise AuthError("HTTPS private key permissions are unsafe")
    checked(["/usr/bin/openssl", "x509", "-in", str(cert), "-noout", "-checkend", "0"])
    start = command(["/usr/bin/openssl", "x509", "-in", str(cert), "-noout", "-startdate"])
    if start.returncode:
        raise AuthError("Invalid HTTPS certificate")
    not_before = datetime.datetime.strptime(start.stdout.strip().split("=", 1)[1], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
    if not_before > datetime.datetime.now(datetime.timezone.utc):
        raise AuthError("HTTPS certificate is not yet valid")
    cert_key = command(["/usr/bin/openssl", "x509", "-in", str(cert), "-pubkey", "-noout"])
    private_key = command(["/usr/bin/openssl", "pkey", "-in", str(key), "-pubout", "-passin", "pass:"])
    if cert_key.returncode or private_key.returncode or cert_key.stdout != private_key.stdout:
        raise AuthError("HTTPS certificate and key do not match")


def remove_gateway(path: Path) -> None:
    if path.exists():
        secure_file(path)
        if not path.read_text().startswith(GATEWAY_MARKER):
            raise AuthError("Unexpected Node-RED gateway configuration")
        path.unlink()


def reload_gateway() -> None:
    checked(["/usr/sbin/nginx", "-t"])
    # Do not wait on a systemctl reload job behind the stopping Node-RED unit.
    checked(["/usr/sbin/nginx", "-s", "reload"])


def gateway_ready() -> bool:
    # Local readiness only; the certificate need not name the loopback IP.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    connection = http.client.HTTPSConnection("127.0.0.1", GATEWAY_PORT, timeout=1, context=context)
    try:
        connection.request("GET", "/admin/settings")
        with connection.getresponse() as response:
            return (response.status == 401 and
                    response.getheader("X-IOT2050-Node-RED-Gate") == "active")
    except (OSError, http.client.HTTPException):
        return False
    finally:
        connection.close()


def gateway_closed() -> bool:
    # The template binds wildcard addresses, so probe both loopback families.
    for host in ("127.0.0.1", "::1"):
        try:
            with socket.create_connection((host, GATEWAY_PORT), timeout=1):
                return False
        except OSError as error:
            if error.errno == errno.ECONNREFUSED:
                continue
            if host == "::1" and error.errno in (errno.EAFNOSUPPORT, errno.EADDRNOTAVAIL, errno.ENETUNREACH):
                continue
            return False
    return True


def wait_for_gateway(probe, error_message) -> None:
    deadline = time.monotonic() + GATEWAY_APPLY_TIMEOUT
    while not probe():
        if time.monotonic() >= deadline:
            raise AuthError(error_message)
        time.sleep(0.2)


def close_gateway() -> None:
    remove_gateway(GATEWAY)
    # A previous reload may have failed after unlink. Always apply the closed
    # configuration on retry, even when there is no file left to remove.
    reload_gateway()
    wait_for_gateway(gateway_closed, "Node-RED HTTPS listener did not close")


def migrate_gateway() -> None:
    """Refresh an existing gate on package upgrade, without starting flows."""
    remove_gateway(LEGACY_GATEWAY)
    remove_gateway(GATEWAY)
    # In a chroot, systemctl may succeed without querying a running manager.
    # Require an actual active state before attempting live gateway operations.
    result = command(["/usr/bin/systemctl", "show", "nginx.service",
                      "--property=ActiveState", "--value"])
    if result.returncode or result.stdout.strip() != "active":
        return
    close_gateway()
    if service_state()["ActiveState"] == "active":
        open_gateway()


def check_start() -> None:
    if not configured():
        raise AuthError("Set an access password in Cockpit before starting Node-RED")
    certificate_check()
    runtime = pwd.getpwnam("nodered")
    if runtime.pw_uid == 0 or runtime.pw_shell != "/usr/sbin/nologin":
        raise AuthError("Node-RED runtime account is unsafe")


def open_gateway() -> None:
    check_start()
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        connection = http.client.HTTPConnection("127.0.0.1", 1881, timeout=1)
        try:
            connection.request("GET", "/admin/settings")
            response = connection.getresponse()
            response.read()
            if response.status == 401:
                break
            raise AuthError("Node-RED did not reject anonymous Admin API access")
        except (OSError, http.client.HTTPException):
            time.sleep(0.5)
        finally:
            connection.close()
    else:
        raise AuthError("Node-RED did not become ready")
    secure_file(TEMPLATE)
    ensure_directory(GATEWAY.parent)
    if GATEWAY.exists():
        close_gateway()
    try:
        atomic_write(GATEWAY, TEMPLATE.read_text(), 0o644)
        reload_gateway()
        wait_for_gateway(gateway_ready, "Node-RED HTTPS gateway did not become ready")
    except Exception:
        close_gateway()
        raise


def activate(actor: str, request: dict[str, object], *, start_runtime: bool = True,
             update_password: bool = False) -> None:
    actor = username(actor)
    if not Path("/usr/bin/node-red").exists():
        raise AuthError("Node-RED is not installed")
    autostart = request.get("autostart", True)
    if type(autostart) is not bool:
        raise AuthError("Invalid startup option")
    with locked():
        was_configured = configured()
        password_only = was_configured and update_password
        if not password_only:
            certificate_check()
            if Path("/root/.node-red").exists():
                raise AuthError("Existing root Node-RED data requires an explicit migration")
            close_gateway()
            systemctl("stop", "node-red.service")
        backend = Backend()
        backend.initialize()
        with backend.locked():
            exists = actor in backend.users()
        if not exists:
            backend.create(actor, request.get("password"))
        elif update_password:
            backend.manage("reset", actor, request.get("password"))
        runtime = pwd.getpwnam("nodered")
        prepare_secret(runtime.pw_gid)
        if password_only:
            return
        try:
            atomic_write(SETTINGS, SETTINGS_TEXT, 0o640, gid=runtime.pw_gid)
            systemctl("restart", "iot2050-node-red-auth.service")
            if start_runtime:
                systemctl("start", "node-red.service")
                systemctl("enable" if autostart else "disable", "node-red.service")
        except Exception:
            systemctl("stop", "node-red.service")
            close_gateway()
            if not was_configured:
                SETTINGS.unlink(missing_ok=True)
                systemctl("disable", "node-red.service")
            raise


def validate_request(request: dict[str, object]) -> str:
    operation = request.get("operation")
    fields = {
        "status": {"operation"}, "activate": {"operation", "password", "autostart"},
        "start": {"operation"}, "stop": {"operation"}, "deactivate": {"operation"},
        "reset-password": {"operation", "password"},
        "save-password": {"operation", "password"},
        "set-autostart": {"operation", "autostart"},
    }
    if not isinstance(operation, str) or operation not in fields or set(request) - fields[operation]:
        raise AuthError("Unsupported Node-RED management request")
    return operation


def dispatch(actor: str, request: dict[str, object]) -> dict[str, object]:
    operation = validate_request(request)
    if operation == "status":
        return status(actor)
    if operation == "activate":
        activate(actor, request)
    elif operation == "reset-password":
        Backend().manage("reset", username(actor), request.get("password"))
    elif operation == "save-password":
        activate(actor, request, start_runtime=False, update_password=True)
    elif operation == "set-autostart":
        enabled = request.get("autostart")
        if type(enabled) is not bool:
            raise AuthError("Invalid startup option")
        with locked():
            if not configured():
                raise AuthError("Set an access password before configuring startup")
            backend = Backend()
            with backend.locked():
                if username(actor) not in backend.users():
                    raise AuthError("Set an access password before configuring startup")
            systemctl("enable" if enabled else "disable", "node-red.service")
    else:
        with locked():
            if operation == "start":
                check_start()
                systemctl("start", "node-red.service")
            else:
                systemctl("stop", "node-red.service")
                close_gateway()
                if operation == "deactivate":
                    if configured():
                        SETTINGS.unlink()
                    systemctl("disable", "node-red.service")
    return status(actor)
