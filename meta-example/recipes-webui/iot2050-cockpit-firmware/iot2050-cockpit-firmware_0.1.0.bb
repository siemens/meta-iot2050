# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT

PR = "1"

DESCRIPTION = "IOT2050 Firmware Center Cockpit plugin"
MAINTAINER = "Siemens AG"

inherit dpkg-raw

DEPENDS = "iot2050-fwmgr"

SRC_URI = " \
    file://manifest.json \
    file://index.html \
    file://firmware.css \
    file://firmware.js \
    "

DEBIAN_DEPENDS = "cockpit, iot2050-fwmgr"

do_install() {
    install -v -d ${D}/usr/share/cockpit/iot2050-firmware/
    install -v -m 644 ${WORKDIR}/manifest.json \
        ${D}/usr/share/cockpit/iot2050-firmware/
    install -v -m 644 ${WORKDIR}/index.html \
        ${D}/usr/share/cockpit/iot2050-firmware/
    install -v -m 644 ${WORKDIR}/firmware.css \
        ${D}/usr/share/cockpit/iot2050-firmware/
    install -v -m 644 ${WORKDIR}/firmware.js \
        ${D}/usr/share/cockpit/iot2050-firmware/
}
