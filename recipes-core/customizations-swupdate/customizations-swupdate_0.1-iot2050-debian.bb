#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DESCRIPTION = "IOT2050 swupdate image customizations"

DEBIAN_DEPENDS = "swupdate"

SRC_URI = " \
    file://swupdate.cfg \
    file://suricatta"

do_install() {
    install -v -d ${D}/etc/swupdate/conf.d
    install -v -m 644 ${WORKDIR}/swupdate.cfg ${D}/etc/
    install -v -m 644 ${WORKDIR}/suricatta ${D}/etc/swupdate/conf.d/
}
