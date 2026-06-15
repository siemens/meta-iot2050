# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 default firewall configuration for the web gateway"

DEBIAN_DEPENDS = "firewalld"

SRC_URI = " \
    file://public.xml \
    "

do_install() {
    install -d -m 755 ${D}/etc/firewalld/zones
    install -m 644 ${WORKDIR}/public.xml ${D}/etc/firewalld/zones/
}
