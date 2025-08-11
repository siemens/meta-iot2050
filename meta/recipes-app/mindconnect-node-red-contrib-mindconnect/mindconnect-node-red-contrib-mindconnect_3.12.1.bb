#
# Copyright (c) Siemens AG, 2020-2025
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

inherit npm
inherit node-red-module

DESCRIPTION = "node red mindconnect node using mindconnect-nodejs library"

NPMPN = "@mindconnect/node-red-contrib-mindconnect"
