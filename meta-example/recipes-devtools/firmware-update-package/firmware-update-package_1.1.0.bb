#
# Copyright (c) Siemens AG, 2023-2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
DESCRIPTION = "Generate The Firmware Update Package"
MAINTAINER = "Li Hua Qian <huaqian.li@siemens.com>"
PR = "1"

inherit dpkg

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

DEPENDS = "u-boot-iot2050"
DEPENDS:append:trust-center = " trust-center-credential trust-center-remote-signer"
DEBIAN_BUILD_DEPENDS:append:trust-center = ", trust-center-credential, trust-center-remote-signer"
SIGNING_METHOD:trust-center ?= "production"

SRC_URI = " \
    file://iot2050-generate-fwu-tarball.sh \
    file://update.conf.json.tmpl \
    file://custMpk.pem \
    file://debian"
SRC_URI:remove:trust-center = " file://custMpk.pem"

S = "${WORKDIR}/${P}"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build[depends] = "u-boot-iot2050:do_deploy"
do_prepare_build() {
    deb_debianize
    rm -f ${S}/debian/compat

    install -m 0644 ${WORKDIR}/debian/${PN}.install ${S}/debian/${PN}.install
    install -m 0755 ${WORKDIR}/debian/rules ${S}/debian/rules
    cp ${WORKDIR}/iot2050-generate-fwu-tarball.sh ${S}/
    cp ${WORKDIR}/update.conf.json.tmpl ${S}/
    cp ${DEPLOY_DIR_IMAGE}/iot2050-pg1-image-boot.bin ${S}/
    rm -f ${S}/iot2050-pg2-image-boot.bin.fwu
    cp ${DEPLOY_DIR_IMAGE}/iot2050-pg2-image-boot.bin ${S}/iot2050-pg2-image-boot.bin.fwu
    dd if=/dev/zero ibs=1 count=65536 | LC_ALL=C tr "\000" "\377" > ${S}/paddedFile.bin
    dd if=${S}/paddedFile.bin of=${S}/iot2050-pg2-image-boot.bin.fwu \
      seek=7077888 bs=1 conv=notrunc
    rm -f ${S}/paddedFile.bin
    cp ${DEPLOY_DIR_IMAGE}/u-boot-initial-env ${S}/

    if [ "${SIGNING_METHOD}" != "production" ]; then
        cp ${WORKDIR}/custMpk.pem ${S}/
    fi

    cat <<EOF > ${S}/vars.mk
ISAR_RELEASE_VERSION := $(${ISAR_RELEASE_CMD})
SIGNING_METHOD := ${SIGNING_METHOD}
EOF
}

do_deploy() {
    dpkg --fsys-tarfile ${WORKDIR}/${PN}_${PV}*.deb | \
        tar xOf - "./usr/share/iot2050/fwu/IOT2050-FW-Update-PKG-$(${ISAR_RELEASE_CMD}).tar.xz" \
        > "${DEPLOY_DIR_IMAGE}/IOT2050-FW-Update-PKG-$(${ISAR_RELEASE_CMD}).tar.xz"
}

addtask deploy after do_dpkg_build before do_build
do_deploy[dirs] = "${DEPLOY_DIR_IMAGE}"
