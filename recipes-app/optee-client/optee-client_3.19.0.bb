#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
#

inherit dpkg

DESCRIPTION = "OPTee Client"

SRC_URI += "https://github.com/OP-TEE/optee_client/archive/${PV}.tar.gz;downloadfilename=${PN}-${PV}.tar.gz \
    file://0001-libteeacl-Move-the-uuid-dev-checking-inside.patch \
    file://0002-makefile-Fix-the-pkg-config-for-cross-building.patch \
    file://control.tmpl \
    file://rules.tmpl \
    file://tee-supplicant.service"
SRC_URI[sha256sum] = "5f0d02efa0e496964e86ca9dd2461ada923d1f9e11a4b9cafb5393bd08337644"

S = "${WORKDIR}/optee_client-${PV}"

TEE_FS_PARENT_PATH ?= "/var/lib/optee-client/data/tee"

TEMPLATE_FILES = "rules.tmpl control.tmpl"
TEMPLATE_VARS += "TEE_FS_PARENT_PATH"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize

    cp -f ${WORKDIR}/tee-supplicant.service \
        ${S}/debian/tee-supplicant.service
    echo "/usr/sbin/*" > ${S}/debian/tee-supplicant.install
    echo "lib/optee_armtz/" > ${S}/debian/tee-supplicant.dirs
    echo "usr/lib/tee-supplicant/plugins/" >> ${S}/debian/tee-supplicant.dirs

    echo "usr/lib/*/libteec*.so.*" > ${S}/debian/libteec1.install

    echo "usr/include/*" > ${S}/debian/optee-client-dev.install
    echo "usr/lib/*/lib*.so" >> ${S}/debian/optee-client-dev.install
}
