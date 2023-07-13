#
# Copyright (c) Siemens AG, 2020-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit npm
inherit node-red-module

DESCRIPTION = "A Node-RED node to communicate via OPC UA based on node-opcua library"

do_prepare_build:append() {
    # x86-64 binary that breaks Debian packaging.
    # Fortunately only needed for npm release packaging.
    rm -f ${D}/${NPM_LOCAL_INSTALL_DIR}/node_modules/node-red-contrib-opcua/node_modules/node-opcua-pki/pkg/pki
}
