#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DESCRIPTION = "Board configuration tools"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI = "file://board-conf-tools  \
           file://board-bootup-configuration.service \
           file://postinst \
           "

RDEPENDS = "mraa"
DEBIAN_DEPENDS = "python3-newt, mraa"

S = "${WORKDIR}/board-conf-tools"

do_install() {
    install -v -d ${D}/usr/bin/
    install -v -d ${D}/etc
    install -v -d ${D}/lib/systemd/system/
    # add board bootup configuration service
    install -v -m 644 ${WORKDIR}/board-bootup-configuration.service ${D}/lib/systemd/system/

    cp -rf  ${WORKDIR}/board-conf-tools ${D}/etc
    ln -sf /etc/board-conf-tools/iot2050setup.py   ${D}/usr/bin/iot2050setup
    ln -sf /etc/board-conf-tools/board-bootup-conf.py   ${D}/usr/bin/board-bootup-configuration
}
