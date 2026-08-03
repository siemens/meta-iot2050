# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT

DESCRIPTION = "IOT2050 firmware manager"
MAINTAINER = "Siemens AG"

inherit dpkg-raw

SRC_URI = " \
    file://iot2050_firmware_manager.py \
    file://iot2050-firmware-manager.py \
    file://iot2050-fwmgr \
    file://iot2050-firmware-manager.service \
    file://iot2050-firmware-manager.socket \
    file://postinst \
    "

DEBIAN_DEPENDS = "python3, systemd, iot2050-firmware-update"

do_install() {
    install -v -d ${D}/usr/lib/python3/dist-packages/
    install -v -m 644 ${WORKDIR}/iot2050_firmware_manager.py \
        ${D}/usr/lib/python3/dist-packages/

    install -v -d ${D}/usr/lib/iot2050/firmware-manager/providers.d/
    install -v -m 755 ${WORKDIR}/iot2050-firmware-manager.py \
        ${D}/usr/lib/iot2050/firmware-manager/

    install -v -d ${D}/usr/sbin/
    install -v -m 755 ${WORKDIR}/iot2050-fwmgr ${D}/usr/sbin/

    install -v -d ${D}/usr/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-firmware-manager.service \
        ${D}/usr/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-firmware-manager.socket \
        ${D}/usr/lib/systemd/system/

}
