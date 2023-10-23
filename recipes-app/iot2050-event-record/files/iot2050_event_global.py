# Copyright (c) Siemens AG, 2023
#
# Authors:
#   Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

# IOT2050 Event API server hostname
EVENT_API_SERVER_HOSTNAME = 'localhost'

# IOT2050 Event API server port
EVENT_API_SERVER_PORT = '5050'

# IOT2050 Event Log identifier
EVENT_IDENTIFIER = 'IOT2050-EventRecord'

# IOT2050 Extended IO API server hostname
EIO_API_SERVER_HOSTNAME = 'localhost'

# IOT2050 Extended IO API server port
EIO_API_SERVER_PORT = '5020'

iot2050_event_api_server = f"{EVENT_API_SERVER_HOSTNAME}:{EVENT_API_SERVER_PORT}"
iot2050_eio_api_server = f"{EIO_API_SERVER_HOSTNAME}:{EIO_API_SERVER_PORT}"
