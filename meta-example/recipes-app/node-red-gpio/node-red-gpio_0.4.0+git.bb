#
# Copyright (c) Siemens AG, 2019-2025
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

inherit dpkg-raw
inherit node-red-module

DESCRIPTION = "node-red-gpio-integration"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI = "git://github.com/node-red/node-red-nodes;protocol=https;branch=master \
    file://0001-mraa-gpio-Change-text-x-red-to-text-html.patch \
    file://0002-mraa-gpio-Pass-settings-from-js-to-html.patch \
    file://0003-mraa-gpio-din-Make-D14-D19-IOT2050-only.patch \
    file://0004-mraa-gpio-din-Fix-the-for-attribute-of-lables.patch \
    file://0005-mraa-gpio-dout-Add-D14-D19-for-IOT2050.patch \
    file://0006-mraa-gpio-Make-led-node-IOT2050-only.patch \
    file://0007-mraa-gpio-Fix-led-label-in-the-flow-editor.patch \
    file://0008-mraa-gpio-Add-support-for-IOT2050-SM.patch \
    file://0009-mraa-gpio-pwm-Set-pin-options-according-to-board-typ.patch \
    "

SRCREV="512697eec4cdd6f988b29fdd324ea5b9dbb0b1ae"

S = "${WORKDIR}/git"
DPKG_ARCH = "all"

do_install() {
    install -v -d ${D}/${NPM_LOCAL_INSTALL_DIR}/node_modules/node-red-node-intel-gpio
    install -v -m 644 ${S}/hardware/intel/* ${D}/${NPM_LOCAL_INSTALL_DIR}/node_modules/node-red-node-intel-gpio
}
