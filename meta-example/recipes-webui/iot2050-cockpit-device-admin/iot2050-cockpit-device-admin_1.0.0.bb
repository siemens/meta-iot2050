#
# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT
#

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 Device Admin Cockpit plugin"
MAINTAINER = "Siemens AG"

DEPENDS = "iot2050-web-gateway-nginx"
DEBIAN_DEPENDS = "cockpit, iot2050-web-gateway-nginx, openssl, python3, systemd"

SRC_URI = " \
    file://manifest.json \
    file://index.html \
    file://device-admin.css \
    file://device-admin.js \
    file://iot2050-device-admin \
    "

do_install() {
    install -d -m 755 ${D}/usr/share/cockpit/iot2050-device-admin
    install -m 644 ${WORKDIR}/manifest.json \
        ${D}/usr/share/cockpit/iot2050-device-admin/
    install -m 644 ${WORKDIR}/index.html \
        ${D}/usr/share/cockpit/iot2050-device-admin/
    install -m 644 ${WORKDIR}/device-admin.css \
        ${D}/usr/share/cockpit/iot2050-device-admin/
    install -m 644 ${WORKDIR}/device-admin.js \
        ${D}/usr/share/cockpit/iot2050-device-admin/

    install -d -m 755 ${D}/usr/sbin
    install -m 755 ${WORKDIR}/iot2050-device-admin \
        ${D}/usr/sbin/iot2050-device-admin

}
