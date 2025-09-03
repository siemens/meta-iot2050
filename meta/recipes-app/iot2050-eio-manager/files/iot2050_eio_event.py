#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
from iot2050_eio_global import EIO_FS_EVENT


def read_eio_event():
    try:
        with open(EIO_FS_EVENT, "r") as f:
            event = f.read()
        return event
    except Exception as e:
        raise Exception(f'{type(e).__name__}: {e}')

