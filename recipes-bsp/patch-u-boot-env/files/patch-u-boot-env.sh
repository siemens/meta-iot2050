#!/bin/sh
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

set -x

SCRIPT="$1"

if [ ! $(fw_printenv sysselect &> /dev/null) ]; then
fw_setenv -s "${SCRIPT}"
fi
