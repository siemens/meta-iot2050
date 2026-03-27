# Copyright (c) Siemens AG, 2024-2026
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
inherit dpkg-raw

DESCRIPTION = "Trust Center PPKI credential for IOT2050"

PR = "1"

SRC_URI:append:trust-center = " \
    file://keystore \
    file://truststore \
    file://trust-center-mpk.crt \
    file://trust-center-smpk.crt \
    file://worker.env \
    "

PACKAGE_ARCH = "${HOST_ARCH}"

do_install:append:trust-center() {
    install -v -d ${D}/usr
    install -v -d ${D}/usr/share
    install -v -d ${D}/usr/share/${PN}

    install -v -m 644 ${WORKDIR}/keystore ${D}/usr/share/${PN}
    install -v -m 644 ${WORKDIR}/truststore ${D}/usr/share/${PN}
    install -v -m 644 ${WORKDIR}/trust-center-mpk.crt ${D}/usr/share/${PN}
    install -v -m 644 ${WORKDIR}/trust-center-smpk.crt ${D}/usr/share/${PN}
    install -v -m 644 ${WORKDIR}/worker.env ${D}/usr/share/${PN}
}
