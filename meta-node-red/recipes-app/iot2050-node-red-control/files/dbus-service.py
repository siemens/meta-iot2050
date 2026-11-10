#!/usr/bin/python3 -I
# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT
import json
import os
from pathlib import Path
import pwd
import resource
import subprocess
import sys

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

sys.path.insert(0, "/usr/lib/iot2050/node-red-auth")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from backend import AuthError, MAX_REQUEST
from control import dispatch, validate_request

NAME = "com.siemens.iot2050.NodeRed"
PATH = "/com/siemens/iot2050/NodeRed"
ACTION = "com.siemens.iot2050.node-red.manage"


class Management(dbus.service.Object):
    def __init__(self, bus: dbus.SystemBus) -> None:
        self.bus = bus
        self.identity = dbus.Interface(bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus"), "org.freedesktop.DBus")
        self.authority = dbus.Interface(bus.get_object("org.freedesktop.PolicyKit1", "/org/freedesktop/PolicyKit1/Authority"), "org.freedesktop.PolicyKit1.Authority")
        super().__init__(dbus.service.BusName(NAME, bus), PATH)

    @dbus.service.method(NAME, in_signature="s", out_signature="s", sender_keyword="sender")
    def Call(self, raw: str, sender: str) -> str:
        return self.invoke(raw, sender, sender)

    @dbus.service.method(NAME, in_signature="ss", out_signature="s", sender_keyword="sender")
    def CallFor(self, original: str, raw: str, sender: str) -> str:
        # A root connection may perform an administrative action on behalf of
        # a still-live original connection. Names/UIDs are resolved by D-Bus,
        # never accepted from a username field or inferred from root itself.
        if int(self.identity.GetConnectionUnixUser(sender)) != 0 or not original.startswith(":"):
            return json.dumps({"ok": False, "error": {"message": "Root authorization is required for delegation."}})
        return self.invoke(raw, sender, original)

    def invoke(self, raw: str, sender: str, original: str) -> str:
        stage = "request"
        try:
            if len(raw.encode()) > MAX_REQUEST:
                raise AuthError("Node-RED request is too large")
            request = json.loads(raw)
            if not isinstance(request, dict):
                raise AuthError("Invalid Node-RED request")
            operation = validate_request(request)
            uid = int(self.identity.GetConnectionUnixUser(original))
            if original != sender and uid == 0:
                raise AuthError("Delegation requires an original non-root connection")
            actor = pwd.getpwuid(uid).pw_name
            if operation != "status":
                stage = "authorization"
                subject = ("system-bus-name", {"name": dbus.String(sender, variant_level=1)})
                allowed, _, _ = self.authority.CheckAuthorization(subject, ACTION, {}, dbus.UInt32(1), "", timeout=120)
                if not allowed:
                    raise AuthError("Administrative authorization is required")
            stage = "execution"
            result = dispatch(actor, request)
            result["caller_connection"] = str(original)
            return json.dumps({"ok": True, "data": result})
        except (AuthError, OSError, ValueError, KeyError, subprocess.SubprocessError, dbus.DBusException) as error:
            print(f"Node-RED management failed at {stage}", file=sys.stderr)
            message = str(error) if isinstance(error, AuthError) else "Node-RED operation failed; check service status."
            return json.dumps({"ok": False, "error": {"message": message}})


def main() -> None:
    if os.getuid() != 0:
        raise RuntimeError("Node-RED management service requires root")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    service = Management(dbus.SystemBus())
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
