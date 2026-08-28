# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""Shared local IPC endpoints for IOT2050 EIO-related services."""

EIO_API_SERVER_SOCKET = "/run/iot2050/eio.sock"
iot2050_eio_api_server = "unix://" + EIO_API_SERVER_SOCKET

EVENT_API_SERVER_SOCKET = "/run/iot2050/event-record.sock"
iot2050_event_api_server = "unix://" + EVENT_API_SERVER_SOCKET

MODULE_FIRMWARE_SOCKET = "/run/iot2050/module-firmware.sock"
iot2050_module_firmware_api_server = "unix://" + MODULE_FIRMWARE_SOCKET
