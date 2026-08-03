# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT

DESCRIPTION = "SM firmware providers for the IOT2050 firmware manager"
MAINTAINER = "Siemens AG"

inherit dpkg-raw

SRC_URI = " \
    file://iot2050_firmware_provider_sm.py \
    file://20-controller.json \
    file://30-module.json \
    "

DEBIAN_DEPENDS = "iot2050-firmware-manager, iot2050-eio-manager, iot2050-eiofsd, iot2050-module-firmware-update"

do_install() {
    install -v -d ${D}/usr/lib/iot2050/firmware-manager/
    install -v -m 644 ${WORKDIR}/iot2050_firmware_provider_sm.py \
        ${D}/usr/lib/iot2050/firmware-manager/

    install -v -d ${D}/usr/lib/iot2050/firmware-manager/providers.d/
    install -v -m 644 ${WORKDIR}/20-controller.json \
        ${D}/usr/lib/iot2050/firmware-manager/providers.d/
    install -v -m 644 ${WORKDIR}/30-module.json \
        ${D}/usr/lib/iot2050/firmware-manager/providers.d/
}
