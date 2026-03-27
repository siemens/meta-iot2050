# Copyright (c) Siemens AG, 2024-2026
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
inherit dpkg-raw

DESCRIPTION = "Trust Center Remote Signer for IOT2050"

PR = "1"

SRC_URI:append:trust-center = " \
    file://tc-signclient \
    file://openssl.conf \
    file://runsignclient.sh \
    file://postinst \
    "

SIGNCLIENT_SRC = "${WORKDIR}/tc-signclient"
S = "${WORKDIR}/source"

PACKAGE_ARCH = "${HOST_ARCH}"

DEPENDS = "extsign-provider trust-center-credential"
DEBIAN_DEPENDS = "extsign-provider, trust-center-credential, \
    default-jre:${PACKAGE_ARCH}, openssl:${PACKAGE_ARCH}"

do_install:append:trust-center() {
    install -v -d ${D}/usr
    install -v -d ${D}/usr/share
    install -v -d ${D}/usr/share/${PN}

    cp -rPf ${SIGNCLIENT_SRC}/. ${D}/usr/share/${PN}/sign-client
    install -v -m 644 ${WORKDIR}/openssl.conf ${D}/usr/share/${PN}
    install -v -m 755 ${WORKDIR}/runsignclient.sh ${D}/usr/share/${PN}

    install -v -d ${D}/var
    install -v -d ${D}/var/spool
    install -v -d ${D}/var/spool/${PN}
    install -v -d ${D}/var/spool/${PN}/in
    install -v -d ${D}/var/spool/${PN}/out
}
