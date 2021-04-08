#!/bin/sh
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

set -e

USTATE="$(fw_printenv -n ustate | tail -1)"
if [ -z "$USTATE" ]; then
    echo "$0: ustate is not set - abort!"
    exit 1
fi

case "$1" in
    success)
        case "$USTATE" in
            0)
                # If no update was pending, ignore this
                exit 0
                ;;
            2)
                fw_setenv ustate 0
                exit 0
                ;;
            *)
                echo "$0: attempt to acknowledge while in wrong state('$USTATE' instead of '0')" >&2
                exit 1
                ;;
        esac
    ;;
    failed)
        case "$USTATE" in
            3)
                fw_setenv ustate 0
                exit 0
                ;;
            *)
                echo "$0: attempt to acknowledge failure while in wrong state('$USTATE' instead of '3')" >&2
                exit 1
                ;;
        esac
        ;;
    *)
        echo "usage: $0 <action>" >&2
        echo "" >&2
        echo "<action>: 'success', 'failed' " >&2
        exit 1
        ;;
esac
