#
# Copyright (c) Siemens AG, 2020-2022
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit npm

DESCRIPTION = "A Node-RED node to communicate via OPC UA based on node-opcua library"

NPM_LOCAL_INSTALL_DIR = "/root/.node-red"

do_prepare_build_append() {
    # x86-64 binary that breaks Debian packaging.
    # Fortunately only needed for npm release packaging.
    rm -f ${D}/root/.node-red/node_modules/node-red-contrib-opcua/node_modules/node-opcua-pki/pkg/pki
}
