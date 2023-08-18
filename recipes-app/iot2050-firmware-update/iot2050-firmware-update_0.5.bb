#
# Copyright (c) Siemens AG, 2020-2023
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

DESCRIPTION = "OSPI Firmware Update Scripts"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI = " \
    file://update.conf.json.tmpl \
    file://iot2050-firmware-update.tmpl"

TEMPLATE_FILES = "update.conf.json.tmpl iot2050-firmware-update.tmpl"

inherit dpkg-raw

DEBIAN_DEPENDS = "python3-progress"

do_install() {
    install -v -d ${D}/usr/lib/iot2050/fwu
    install -v -m 644 ${WORKDIR}/update.conf.json ${D}/usr/lib/iot2050/fwu/
    install -v -m 755 ${WORKDIR}/iot2050-firmware-update ${D}/usr/lib/iot2050/fwu/

    install -v -d ${D}/usr/sbin/
    ln -sf ../lib/iot2050/fwu/iot2050-firmware-update ${D}/usr/sbin/iot2050-firmware-update
}

do_deploy_deb:append() {
    cp -f "${WORKDIR}/${PN}_${PV}_arm64.deb" "${DEPLOY_DIR_IMAGE}/"
}

do_deploy_deb[dirs] = "${DEPLOY_DIR_IMAGE}"
