#
# Copyright (c) Siemens AG, 2020-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit node-red-module
inherit npm

DESCRIPTION = "Node-RED nodes to talk to serial ports"

do_prepare_build:append() {
    sed -i '/override_dh_install:/a\\trm -r ${PP}/image/${NPM_LOCAL_INSTALL_DIR}/node_modules/node-red-node-serialport/node_modules/@serialport/bindings-cpp/prebuilds' \
        ${S}/debian/rules
}
