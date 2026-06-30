#
# Copyright (c) Siemens AG, 2020-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

inherit npm
inherit node-red-module
DEBIAN_BUILD_DEPENDS = "python3-setuptools"
DESCRIPTION = "A sqlite node for Node-RED"
