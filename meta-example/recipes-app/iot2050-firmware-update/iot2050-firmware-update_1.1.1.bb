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
    file://iot2050_firmware_update.py \
    file://iot2050-firmware-update.tmpl \
    file://iot2050-system-firmware.service \
    file://grpc/iot2050-system-firmware.proto \
    file://grpc/iot2050_system_firmware_pb2.py \
    file://grpc/iot2050_system_firmware_pb2_grpc.py \
    file://custMpk.crt"
SRC_URI:append:trust-center = " file://tc-pub.pem"
SRC_URI:remove:trust-center = " file://custMpk.crt"

OS_VERSION_KEY ?= "BUILD_ID"
MIN_OS_VERSION ?= "V01.01.01"

TEMPLATE_FILES = "update.conf.json.tmpl iot2050-firmware-update.tmpl"
TEMPLATE_VARS += "OS_VERSION_KEY MIN_OS_VERSION IMAGE_FULLNAME"

DPKG_ARCH = "any"

inherit dpkg-raw

DEBIAN_DEPENDS = "python3-cryptography, python3-grpcio, python3-packaging, u-boot-tools, iot2050-firmware-common"
DEBIAN_BUILD_DEPENDS = "openssl"

do_install() {
    install -v -d ${D}/usr/sbin/
    install -v -m 755 ${WORKDIR}/iot2050-firmware-update \
        ${D}/usr/sbin/iot2050-firmware-update

    install -v -d ${D}/usr/lib/python3/dist-packages/
    install -v -m 644 ${WORKDIR}/iot2050_firmware_update.py \
        ${D}/usr/lib/python3/dist-packages/iot2050_firmware_update.py
    install -v -m 644 ${WORKDIR}/grpc/iot2050_system_firmware_pb2.py \
        ${D}/usr/lib/python3/dist-packages/iot2050_system_firmware_pb2.py
    install -v -m 644 ${WORKDIR}/grpc/iot2050_system_firmware_pb2_grpc.py \
        ${D}/usr/lib/python3/dist-packages/iot2050_system_firmware_pb2_grpc.py

    install -v -d ${D}/usr/lib/systemd/system
    install -v -m 644 ${WORKDIR}/iot2050-system-firmware.service \
        ${D}/usr/lib/systemd/system/

    install -v -d ${D}/usr/share/iot2050/fwu
    install -v -m 644 ${WORKDIR}/update.conf.json ${D}/usr/share/iot2050/fwu/

    if [ -f ${WORKDIR}/tc-pub.pem ]; then
        cp ${WORKDIR}/tc-pub.pem ${WORKDIR}/public.key
    else
        openssl x509 -in ${WORKDIR}/custMpk.crt -pubkey -noout > ${WORKDIR}/public.key
    fi

    install -v -d ${D}/usr/share/iot2050/fwu
    install -v -m 644 ${WORKDIR}/public.key ${D}/usr/share/iot2050/fwu/
}

do_deploy_deb:append() {
    cp -f "${WORKDIR}/${PN}_${PV}_arm64.deb" "${DEPLOY_DIR_IMAGE}/"
}

do_deploy_deb[dirs] = "${DEPLOY_DIR_IMAGE}"
