#!/bin/sh
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT
SCRIPT="$1"
# use grep and cut to strip away environment status and get the value
# of sysselect
key="sysselect"
sysselect_value=$(fw_printenv "${key}" | grep "${key}" | cut -d= -f2)

if [ -z "${sysselect_value}" ]; then
    if ! fw_setenv -s "${SCRIPT}"; then
        echo "$0: could not patch u-boot firmware"
        exit 1
    fi
fi
