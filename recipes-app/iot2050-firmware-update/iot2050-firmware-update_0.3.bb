#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

DESCRIPTION = "OSPI Firmware Update Scripts"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI = "file://iot2050-firmware-update"

inherit dpkg-raw

do_install() {
    install -v -d ${D}/usr/sbin/
    install -v -m 755 ${WORKDIR}/iot2050-firmware-update ${D}/usr/sbin/
}

do_deploy_deb_append() {
    cp -f "${WORKDIR}/${PN}_${PV}_arm64.deb" "${DEPLOY_DIR_IMAGE}/"
}

do_deploy_deb[dirs] = "${DEPLOY_DIR_IMAGE}"
