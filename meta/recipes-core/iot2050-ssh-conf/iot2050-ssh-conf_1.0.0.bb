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

DESCRIPTION = "IOT2050 SSH configuration"

DEBIAN_DEPENDS = "openssh-server"

SRC_URI = " \
    file://etc/ssh/sshd_config.d/50-iot2050-product-security.conf \
"

do_install() {
    install -d -m 755 ${D}/etc/ssh/sshd_config.d
    install -m 644 ${WORKDIR}/etc/ssh/sshd_config.d/50-iot2050-product-security.conf ${D}/etc/ssh/sshd_config.d/
}