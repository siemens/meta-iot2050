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

DESCRIPTION = "The all in one Modbus TCP and Serial contribution package for Node-RED"

do_prepare_build:append() {
    sed -i '/override_dh_install:/a\\trm -r ${PP}/image/${NPM_LOCAL_INSTALL_DIR}/node_modules/node-red-contrib-modbus/node_modules/serialport/node_modules/@serialport/bindings-cpp/prebuilds' \
        ${S}/debian/rules
}
