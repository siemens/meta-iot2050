#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit npm

DESCRIPTION = "The all in one Modbus TCP and Serial contribution package for Node-RED"

DEBIAN_BUILD_DEPENDS =. "libnode-dev,"

NPM_LOCAL_INSTALL_DIR = "/root/.node-red"
