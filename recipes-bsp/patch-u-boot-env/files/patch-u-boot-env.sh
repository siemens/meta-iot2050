#!/bin/sh
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

if [ -z "$(fw_printenv -n "$1")" ]; then
    if ! fw_setenv -s "$2"; then
        echo "$0: could not patch u-boot firmware"
        exit 1
    fi
fi
