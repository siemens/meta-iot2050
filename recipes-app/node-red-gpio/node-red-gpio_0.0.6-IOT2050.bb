#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DESCRIPTION = "node-red-gpio-integration"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI = " \
    git://github.com/node-red/node-red-nodes;protocol=https \
    file://0001-add-the-board-info-add-the-led-control-node.patch \
    file://0002-extend-gpio-to-D19.patch \
    file://0003-Clean-up-mraa-objects-on-node-closing.patch \
    file://0004-Add-USER-button.patch \
    file://0005-Add-configurable-GPIO-mode-for-DIN.patch \
    file://0006-node-red-gpio-Add-support-for-initial-message-from.patch"
SRCREV="3087e8e2a1ea189f394bca0a2af159ad859d7722"

S = "${WORKDIR}/git"

DEBIAN_DEPENDS = "node-red"

do_install() {
    install -v -d ${D}/usr/lib/node_modules/node-red/node_modules/node-red-node-intel-gpio
    install -v -m 644 ${S}/hardware/intel/* ${D}/usr/lib/node_modules/node-red/node_modules/node-red-node-intel-gpio
}
