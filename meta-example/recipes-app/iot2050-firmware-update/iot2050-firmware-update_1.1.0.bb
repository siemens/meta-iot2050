#
# Copyright (c) Siemens AG, 2020-2025
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

DESCRIPTION = "OSPI Firmware Update Scripts"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI = " \
    file://update.conf.json.tmpl \
    file://iot2050-firmware-update.tmpl \
    file://custMpk.crt"

OS_VERSION_KEY ?= "BUILD_ID"
MIN_OS_VERSION ?= "V01.01.01"

TEMPLATE_FILES = "update.conf.json.tmpl iot2050-firmware-update.tmpl"
TEMPLATE_VARS += "OS_VERSION_KEY MIN_OS_VERSION IMAGE_FULLNAME"

DPKG_ARCH = "any"

inherit dpkg-raw

DEBIAN_DEPENDS = "python3-cryptography, python3-progress, python3-packaging, u-boot-tools"
DEBIAN_BUILD_DEPENDS = "openssl"

do_install() {
    install -v -d ${D}/usr/sbin/
    install -v -m 755 ${WORKDIR}/iot2050-firmware-update ${D}/usr/sbin/

    install -v -d ${D}/usr/share/iot2050/fwu
    install -v -m 644 ${WORKDIR}/update.conf.json ${D}/usr/share/iot2050/fwu/
   
    openssl x509 -in ${WORKDIR}/custMpk.crt -pubkey -noout > ${WORKDIR}/public.key
    install -v -d ${D}/usr/share/iot2050/fwu
    install -v -m 644 ${WORKDIR}/public.key ${D}/usr/share/iot2050/fwu/
}

do_deploy_deb:append() {
    cp -f "${WORKDIR}/${PN}_${PV}_arm64.deb" "${DEPLOY_DIR_IMAGE}/"
}

do_deploy_deb[dirs] = "${DEPLOY_DIR_IMAGE}"
