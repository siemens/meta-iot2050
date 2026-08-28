# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""Shared deployment paths for System Firmware services and clients.

These values are a package boundary contract between the System Firmware
service, the /usr/sbin/iot2050-firmware-update CLI, and the fwmgr system
backend. Keep them in one importable module so every participant uses the
same paths and limits.
"""

SYSTEM_FIRMWARE_SOCKET_PATH = "/run/iot2050/system-firmware.sock"
SYSTEM_FIRMWARE_SOCKET_TARGET = "unix://" + SYSTEM_FIRMWARE_SOCKET_PATH

DEFAULT_FIRMWARE_DIR = "/usr/share/iot2050/fwu"
DEFAULT_FIRMWARE_PATTERN = "IOT2050-FW-Update-PKG-*.tar.xz"
DEFAULT_MAX_FIRMWARE_SIZE = 64 * 1024 * 1024
