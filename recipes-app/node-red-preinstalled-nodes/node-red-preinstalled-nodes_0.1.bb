#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DPKG_ARCH = "all"

REGULAR_NODE_RED_PACKAGES = " \
    node-red-dashboard \
    node-red-contrib-opcua \
    node-red-contrib-modbus \
    node-red-contrib-s7 \
    node-red-node-serialport \
    node-red-node-sqlite \
    "

NODE_RED_PACKAGES = " \
    ${REGULAR_NODE_RED_PACKAGES} \
    @mindconnect/node-red-contrib-mindconnect"

RDEPENDS = " \
    ${REGULAR_NODE_RED_PACKAGES} \
    mindconnect-node-red-contrib-mindconnect"

DEBIAN_DEPENDS = " \
    ${@','.join(d.getVar('REGULAR_NODE_RED_PACKAGES', d).split())}, \
    mindconnect-node-red-contrib-mindconnect"
