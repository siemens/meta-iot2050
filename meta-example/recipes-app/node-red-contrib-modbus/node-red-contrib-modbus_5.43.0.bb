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

DESCRIPTION = "The all in one Modbus TCP and Serial contribution package for Node-RED"

do_prepare_build:append() {
    sed -i '/override_dh_install:/a\\trm -r ${PP}/image/${NPM_LOCAL_INSTALL_DIR}/node_modules/node-red-contrib-modbus/node_modules/@openp4nr/modbus-serial/node_modules/@serialport/bindings-cpp/prebuilds' \
        ${S}/debian/rules
}