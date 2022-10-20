#
# Copyright (c) Siemens AG, 2019-2022
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

SRC_URI = "git://github.com/node-red/node-red-nodes;protocol=https"

SRCREV="c15fa79e9535d029d206dfb76474d56bf979504b"

S = "${WORKDIR}/git"

DEBIAN_DEPENDS = "node-red"

do_install() {
    install -v -d ${D}/usr/lib/node_modules/node-red/node_modules/node-red-node-intel-gpio
    install -v -m 644 ${S}/hardware/intel/* ${D}/usr/lib/node_modules/node-red/node_modules/node-red-node-intel-gpio
}
