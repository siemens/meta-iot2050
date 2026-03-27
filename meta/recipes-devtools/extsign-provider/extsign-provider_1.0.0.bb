# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
inherit dpkg

DESCRIPTION = "The External Signer OpenSSL provider"

SRC_URI = " \
    file://extsign_provider.c;subdir=extsign-provider/src \
    file://debian/rules \
    "

S = "${WORKDIR}/extsign-provider"

PACKAGE_ARCH = "${HOST_ARCH}"

DEBIAN_BUILD_DEPENDS = "libssl-dev:native"
DEBIAN_DEPENDS = "libssl3"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize
    install -m 0755 ${WORKDIR}/debian/rules ${S}/debian/rules

    rm -f ${S}/debian/extsign-provider.install
    echo "run/extsign_provider.so /usr/lib/extsign-provider" > ${S}/debian/extsign-provider.install
}
