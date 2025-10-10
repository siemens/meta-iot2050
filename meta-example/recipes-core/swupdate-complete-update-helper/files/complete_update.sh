#!/bin/sh
#
# Copyright (c) Siemens AG, 2021-2023
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

set -e

eval $(bg_printenv -c -o ustate -r)
if [ -z "$USTATE" ]; then
    echo "$0: EFI Boot Guard is not configured - abort!"
    exit 1
fi

case "$USTATE" in
0)
    # If no update was pending, ignore this
    exit 0
    ;;
2)
    bg_setenv -c
    exit 0
    ;;
*)
    echo "$0: attempt to acknowledge while in wrong state('$USTATE' instead of '2')" >&2
    exit 1
    ;;
esac
