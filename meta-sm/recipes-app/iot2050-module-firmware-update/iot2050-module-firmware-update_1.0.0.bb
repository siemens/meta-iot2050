#
# Copyright (c) Siemens AG, 2024-2025
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

DESCRIPTION = "IOT2050 Customized External Signal Module Firmware Update"
MAINTAINER = "huaqian.li@siemens.com"
DEBIAN_DEPENDS = "iot2050-firmware-common, iot2050-eio-common, iot2050-eiofsd, python3-grpcio"

SRC_URI = " \
    file://iot2050_module_firmware_update.py \
    file://iot2050-module-firmware-update.tmpl \
    file://iot2050-module-firmware.service \
    file://grpc/iot2050-module-firmware.proto \
    file://grpc/iot2050_module_firmware_pb2.py \
    file://grpc/iot2050_module_firmware_pb2_grpc.py \
    file://grpc/iot2050_module_firmware_pb2.pyi"

TEMPLATE_FILES = "iot2050-module-firmware-update.tmpl"

inherit dpkg-raw

do_install() {
    install -v -d ${D}/usr/sbin/
    install -v -m 755 ${WORKDIR}/iot2050-module-firmware-update ${D}/usr/sbin/

    install -v -d ${D}/usr/lib/python3/dist-packages/
    install -v -m 644 ${WORKDIR}/iot2050_module_firmware_update.py \
        ${D}/usr/lib/python3/dist-packages/

    install -v -m 644 ${WORKDIR}/grpc/iot2050_module_firmware_pb2.py \
        ${D}/usr/lib/python3/dist-packages/
    install -v -m 644 ${WORKDIR}/grpc/iot2050_module_firmware_pb2_grpc.py \
        ${D}/usr/lib/python3/dist-packages/
    install -v -m 644 ${WORKDIR}/grpc/iot2050_module_firmware_pb2.pyi \
        ${D}/usr/lib/python3/dist-packages/

    install -v -d ${D}/usr/lib/iot2050/module-firmware/grpc
    install -v -m 644 ${WORKDIR}/grpc/iot2050-module-firmware.proto \
        ${D}/usr/lib/iot2050/module-firmware/grpc/

    install -v -d ${D}/usr/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-module-firmware.service \
        ${D}/usr/lib/systemd/system/
}

do_deploy_deb[dirs] = "${DEPLOY_DIR_IMAGE}"
