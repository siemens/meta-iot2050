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
    file://iot2050-module-firmware-service.py \
    file://iot2050-module-firmware-update.tmpl \
    file://iot2050-module-firmware.service \
    file://gRPC/iot2050-module-firmware.proto \
    file://gRPC/iot2050_module_firmware_pb2.py \
    file://gRPC/iot2050_module_firmware_pb2_grpc.py \
    file://gRPC/iot2050_module_firmware_pb2.pyi"

TEMPLATE_FILES = "iot2050-module-firmware-update.tmpl"

inherit dpkg-raw

do_install() {
    install -v -d ${D}/usr/lib/iot2050/module-firmware/
    install -v -m 755 ${WORKDIR}/iot2050-module-firmware-update \
        ${D}/usr/lib/iot2050/module-firmware/
    install -v -m 755 ${WORKDIR}/iot2050-module-firmware-service.py \
        ${D}/usr/lib/iot2050/module-firmware/

    install -v -d ${D}/usr/sbin/
    ln -sf ../lib/iot2050/module-firmware/iot2050-module-firmware-update \
        ${D}/usr/sbin/iot2050-module-firmware-update
    install -v -d ${D}/usr/bin/
    ln -sf ../lib/iot2050/module-firmware/iot2050-module-firmware-service.py \
        ${D}/usr/bin/iot2050-module-firmware-service

    install -v -d ${D}/usr/lib/iot2050/module-firmware/gRPC/
    install -v -m 755 ${WORKDIR}/gRPC/iot2050_module_firmware_pb2.py \
        ${D}/usr/lib/iot2050/module-firmware/gRPC/
    install -v -m 755 ${WORKDIR}/gRPC/iot2050_module_firmware_pb2_grpc.py \
        ${D}/usr/lib/iot2050/module-firmware/gRPC/
    install -v -m 755 ${WORKDIR}/gRPC/iot2050_module_firmware_pb2.pyi \
        ${D}/usr/lib/iot2050/module-firmware/gRPC/
    install -v -m 755 ${WORKDIR}/gRPC/iot2050-module-firmware.proto \
        ${D}/usr/lib/iot2050/module-firmware/gRPC/

    install -v -d ${D}/usr/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-module-firmware.service \
        ${D}/usr/lib/systemd/system/
}

do_deploy_deb[dirs] = "${DEPLOY_DIR_IMAGE}"
