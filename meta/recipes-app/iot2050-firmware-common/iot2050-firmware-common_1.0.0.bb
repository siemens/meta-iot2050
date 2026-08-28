# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT

PR = "1"

DESCRIPTION = "Shared Python helpers for IOT2050 firmware services"
MAINTAINER = "Siemens AG"

inherit dpkg-raw

SRC_URI = " \
    file://iot2050_firmware_global.py \
    file://iot2050_firmware_operation_store.py \
    "

DEBIAN_DEPENDS = "python3"

do_install() {
    install -v -d ${D}/usr/lib/python3/dist-packages/
    install -v -m 644 ${WORKDIR}/iot2050_firmware_global.py \
        ${D}/usr/lib/python3/dist-packages/
    install -v -m 644 ${WORKDIR}/iot2050_firmware_operation_store.py \
        ${D}/usr/lib/python3/dist-packages/
}
