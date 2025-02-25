#!/bin/sh
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

if ! fw_setenv -s "$2"; then
        echo "$0: Failed to apply config file $2"
        exit 1
fi

watchdog_timer="60000"
current_value=$(fw_printenv -n "$1" 2>/dev/null || echo "")
if [ "$current_value" != "$watchdog_timer" ]; then
        echo "$0: Failed to set $1 to $expected_value (got $current_value)"
        exit 1
fi
