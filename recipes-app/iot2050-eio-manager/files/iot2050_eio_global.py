# Copyright (c) Siemens AG, 2023-2024
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
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

    # Extended IO FUSE filesystem path for configuration
    'EIO_FS_CONTROL': '/eiofs/controller/control',
    'EIO_FS_CONFIG': '/eiofs/controller/config',

    # Extended IO FUSE filesystem path for eio events
    'EIO_FS_EVENT': '/eiofs/log/event',

    # Extended IO FUSE filesystem path for firmware version
    'EIO_FS_FW_VER': '/eiofs/proc/version',

    # EIO Firmware Update: metadata
    'EIO_FWU_META': '/usr/lib/iot2050/eio/firmware-version',

    # EIO Firmware Update: Firmware binary file
    'EIO_FWU_MAP3_FW_BIN': '/usr/lib/iot2050/eio/map3-fw.bin',

    # JSON schema files for validating the config yaml
    'EIO_SCHEMA_ROOT': '/usr/lib/iot2050/eio/schema',

    # template file for yaml config
    'EIO_CONFIG_TEMP_ROOT': '/usr/lib/iot2050/eio/config-template'
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
EIO_FS_CONTROL = effective_conf['EIO_FS_CONTROL']
EIO_FS_CONFIG = effective_conf['EIO_FS_CONFIG']
EIO_FS_EVENT = effective_conf['EIO_FS_EVENT']
EIO_FS_FW_VER = effective_conf['EIO_FS_FW_VER']
EIO_FWU_META = effective_conf['EIO_FWU_META']
EIO_FWU_MAP3_FW_BIN = effective_conf['EIO_FWU_MAP3_FW_BIN']
EIO_SCHEMA_ROOT = effective_conf['EIO_SCHEMA_ROOT']
EIO_CONFIG_TEMP_ROOT = effective_conf['EIO_CONFIG_TEMP_ROOT']

eio_schema_top = f"{EIO_SCHEMA_ROOT}/schema-sm-config.yaml"
eio_schema_refs = [
    f"{EIO_SCHEMA_ROOT}/schema-na.yaml",
    f"{EIO_SCHEMA_ROOT}/schema-sm1223-di-dq.yaml",
    f"{EIO_SCHEMA_ROOT}/schema-sm1231-ai.yaml",
    f"{EIO_SCHEMA_ROOT}/schema-sm1231-rtd.yaml",
    f"{EIO_SCHEMA_ROOT}/schema-sm-sens-di.yaml",
    f"{EIO_SCHEMA_ROOT}/schema-sm1238-em-480vac.yaml",
    f"{EIO_SCHEMA_ROOT}/schema-sm1221-8di.yaml"
]

eio_conf_templates = [
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7223-1QH32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7223-1PL32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7231-4HF32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7231-5PD32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7231-5PF32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7647-0CM00-1AA2.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7238-5XA32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7231-4HD32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-6ES7221-1BF32-0XB0.yaml",
    f"{EIO_CONFIG_TEMP_ROOT}/mlfb-NA.yaml"
]

iot2050_eio_api_server = f"{EIO_API_SERVER_HOSTNAME}:{EIO_API_SERVER_PORT}"
