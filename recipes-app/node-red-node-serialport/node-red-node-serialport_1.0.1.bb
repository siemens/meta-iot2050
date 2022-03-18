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

DESCRIPTION = "Node-RED nodes to talk to serial ports"

NPM_LOCAL_INSTALL_DIR = "/root/.node-red"

do_install_append() {
    rm -rf $(find ${D} -name prebuilds -type d)
}
