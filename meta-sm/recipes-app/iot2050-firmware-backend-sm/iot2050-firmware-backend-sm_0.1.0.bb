# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT

PR = "1"

DESCRIPTION = "SM firmware backends for the IOT2050 firmware task core"
MAINTAINER = "Siemens AG"

inherit dpkg-raw

DEPENDS = "iot2050-fwmgr iot2050-eio-manager iot2050-eio-common iot2050-eiofsd iot2050-module-firmware-update"

SRC_URI = " \
    file://iot2050_firmware_backend_sm.py \
    file://20-controller.json \
    file://30-module.json \
    "

DEBIAN_DEPENDS = "iot2050-fwmgr, iot2050-eio-manager, iot2050-eio-common, iot2050-eiofsd, iot2050-module-firmware-update"

do_install() {
    install -v -d ${D}/usr/lib/iot2050/fwmgr/
    install -v -m 644 ${WORKDIR}/iot2050_firmware_backend_sm.py \
        ${D}/usr/lib/iot2050/fwmgr/

    install -v -d ${D}/usr/lib/iot2050/fwmgr/backends.d/
    install -v -m 644 ${WORKDIR}/20-controller.json \
        ${D}/usr/lib/iot2050/fwmgr/backends.d/
    install -v -m 644 ${WORKDIR}/30-module.json \
        ${D}/usr/lib/iot2050/fwmgr/backends.d/
}
