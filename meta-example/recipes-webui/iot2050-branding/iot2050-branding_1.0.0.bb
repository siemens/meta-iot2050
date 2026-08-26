#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 shared branding assets"
MAINTAINER = "Li Hua Qian <huaqian.li@siemens.com>"

SRC_URI = " \
    file://logo/sie-logo-petrol-rgb.svg \
    "

do_install() {
    install -d -m 755 ${D}/usr/share/iot2050/branding/logo
    install -m 644 ${WORKDIR}/logo/sie-logo-petrol-rgb.svg \
        ${D}/usr/share/iot2050/branding/logo/sie-logo-petrol-rgb.svg
}
