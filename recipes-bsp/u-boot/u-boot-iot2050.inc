#
# Copyright (c) Siemens AG, 2019-2022
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-bsp/u-boot/u-boot-custom.inc

PRODUCT_GENERATION = "${@d.getVar('PN').split('-')[3]}"

SRC_URI += " \
    file://rules.tmpl \
    file://prebuild \
    file://fw_env.config"
SRC_URI_append_secureboot = " \
    file://keys/custMpk.crt \
    file://keys/custMpk.key \
    file://keys/custMpk.pem \
    file://keys/x509-sysfw-template.txt \
    file://secure-boot.cfg"
SRC_URI_append_otpcmd = " \
    file://otpcmd.cfg"

U_BOOT_BIN = "flash.bin"
U_BOOT_ENV = "u-boot-initial-env"

SPI_FLASH_IMG = "${U_BOOT_BIN}"
SPI_FLASH_DEPLOY_IMG ??= "iot2050-image-boot.bin"

# Needed to resolve races as long as the layer has to rebuild swig
DEPENDS += "swig"

# Build environment
DEPENDS += "trusted-firmware-a-iot2050 optee-os-iot2050 k3-rti-wdt"
DEBIAN_BUILD_DEPENDS =. "openssl, libssl-dev:native, libssl-dev:arm64, \
    trusted-firmware-a-iot2050, optee-os-iot2050, k3-rti-wdt, \
    swig, python3-dev:native, python3-pkg-resources,"
DEBIAN_BUILD_DEPENDS_append_secureboot = ", python3-pycryptodome:native, \
    pesign, python3-openssl:native"

DEPENDS_append_otpcmd = " secure-boot-otp-provisioning"
DEBIAN_BUILD_DEPENDS_append_otpcmd = ", secure-boot-otp-provisioning"

TEMPLATE_FILES += "rules.tmpl"
TEMPLATE_VARS += "FIRMWARE_SECURE_VER"

U_BOOT_CONFIG_PACKAGE = "1"

do_prepare_build_append() {
    ln -f ${WORKDIR}/prebuild/* ${S}
    ln -sf /lib/firmware/k3-rti-wdt.fw ${S}
    echo "${SPI_FLASH_IMG} /usr/lib/u-boot/${MACHINE}" > \
        ${S}/debian/u-boot-${MACHINE}.install
    echo -$(${ISAR_RELEASE_CMD}) > ${S}/.scmversion
    cp ${WORKDIR}/rules ${S}/debian/rules
    rm -rf ${S}/keys
}

do_prepare_build_append_secureboot() {
    if [ "${PRODUCT_GENERATION}" = "pg1" ]; then
        bbwarn "PG1 devices are not supported in booting securely"
    fi
    mkdir -p ${S}/keys
    ln -f ${WORKDIR}/keys/* ${S}/keys/
    sed -ni '/### Secure boot config/q;p' ${S}/configs/${U_BOOT_CONFIG}
    cat ${WORKDIR}/secure-boot.cfg >> ${S}/configs/${U_BOOT_CONFIG}
}

dpkg_runbuild_append_secureboot() {
    # remove private keys from source archive
    gunzip ${WORKDIR}/${PN}_${PV}.tar.gz
    tar --delete -f ${WORKDIR}/${PN}_${PV}.tar u-boot-${PV}/keys/custMpk.key u-boot-${PV}/keys/custMpk.pem
    gzip ${WORKDIR}/${PN}_${PV}.tar
}

do_prepare_build_append_otpcmd() {
    if [ "${PRODUCT_GENERATION}" = "pg1" ]; then
        bbwarn "PG1 devices are not supported in booting securely"
    fi
    ln -sf /usr/lib/secure-boot-otp-provisioning/otpcmd.bin ${S}
    sed -ni '/### OTP command config/q;p' ${S}/configs/${U_BOOT_CONFIG}
    cat ${WORKDIR}/otpcmd.cfg >> ${S}/configs/${U_BOOT_CONFIG}
}

do_deploy() {
    dpkg --fsys-tarfile ${WORKDIR}/u-boot-${MACHINE}_${PV}*.deb | \
        tar xOf - "./usr/lib/u-boot/${MACHINE}/${U_BOOT_BIN}" \
        > "${DEPLOY_DIR_IMAGE}/${SPI_FLASH_DEPLOY_IMG}"
    dpkg --fsys-tarfile ${WORKDIR}/u-boot-${MACHINE}-config_${PV}*.deb | \
        tar xOf - "./etc/${U_BOOT_ENV}" \
        > "${DEPLOY_DIR_IMAGE}/${U_BOOT_ENV}"
}

addtask deploy after do_dpkg_build before do_build
do_deploy[dirs] = "${DEPLOY_DIR_IMAGE}"
