# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
from dotenv import dotenv_values

default_conf = {
    # IOT2050 Extended IO API server hostname
    'EIO_API_SERVER_HOSTNAME': 'localhost',

    # IOT2050 Extended IO API server port
    'EIO_API_SERVER_PORT': '5020',

    # Periodically syncing timestamp to Extended IO controller
    'EIO_TIME_SYNC_INTERVAL': 30,

    # Extended IO FUSE filesystem path for timestamp syncing
    'EIO_FS_TIMESTAMP': '/eiofs/proc/datetime',
}

local_conf = dotenv_values(".env")

effective_conf = {
    **default_conf,
    **local_conf
}

EIO_API_SERVER_HOSTNAME = effective_conf['EIO_API_SERVER_HOSTNAME']
EIO_API_SERVER_PORT = effective_conf['EIO_API_SERVER_PORT']
EIO_TIME_SYNC_INTERVAL =  effective_conf['EIO_TIME_SYNC_INTERVAL']
EIO_FS_TIMESTAMP = effective_conf['EIO_FS_TIMESTAMP']

iot2050_eio_api_server = f"{EIO_API_SERVER_HOSTNAME}:{EIO_API_SERVER_PORT}"
