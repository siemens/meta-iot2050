# Copyright (c) Siemens AG, 2023
#
# Authors:
#   Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

from iot2050_eio_common import (
    EIO_API_SERVER_SOCKET as DEFAULT_EIO_API_SERVER_SOCKET,
    EVENT_API_SERVER_SOCKET as DEFAULT_EVENT_API_SERVER_SOCKET,
    iot2050_eio_api_server,
    iot2050_event_api_server,
)

# IOT2050 Event Log identifier
EVENT_IDENTIFIER = 'IOT2050-EventRecord'

# Root-only Unix socket used by the local event gRPC service.
EVENT_API_SERVER_SOCKET = DEFAULT_EVENT_API_SERVER_SOCKET

# Root-only Unix socket used by the local EIO gRPC service.
EIO_API_SERVER_SOCKET = DEFAULT_EIO_API_SERVER_SOCKET
