#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-bsp/u-boot/u-boot-custom.inc

SRC_URI += " \
    file://rules.tmpl \
    file://prebuild \
    file://fw_env.config"
SRC_URI:append:secureboot = " \
    file://keys/custMpk.crt \
    file://keys/custMpk.key \
    file://keys/custMpk.pem \
    file://secure-boot.cfg"
SRC_URI:append:otpcmd = " \
    file://otpcmd.cfg"
SRC_URI:append:rpmb-setup = " \
    file://rpmb-setup.cfg"

U_BOOT_BIN = "flash.bin"
U_BOOT_ENV = "u-boot-initial-env"
U_BOOT_CONFIG = "iot2050_defconfig"

# Build environment
DEPENDS += "trusted-firmware-a-iot2050 optee-os-iot2050 k3-rti-wdt"
DEBIAN_BUILD_DEPENDS =. "openssl, libssl-dev:native, libssl-dev:arm64, \
    trusted-firmware-a-iot2050, optee-os-iot2050, k3-rti-wdt, \
    swig, python3-dev:native, python3-pkg-resources, python3-setuptools, \
    python3-pyelftools,"
DEBIAN_BUILD_DEPENDS:append:secureboot = ", python3-pycryptodome:native, \
    pesign, python3-openssl:native"

DEPENDS:append:otpcmd = " secure-boot-otp-provisioning"
DEBIAN_BUILD_DEPENDS:append:otpcmd = ", secure-boot-otp-provisioning"

SB_SIGN = "0"
SB_SIGN:secureboot = "1"

TEMPLATE_FILES += "rules.tmpl"
TEMPLATE_VARS += "FIRMWARE_SECURE_VER SB_SIGN"

U_BOOT_CONFIG_PACKAGE = "1"

do_prepare_build:append() {
    ln -f ${WORKDIR}/prebuild/* ${S}
    ln -sf /lib/firmware/k3-rti-wdt.fw ${S}
    echo "flash-pg1.bin /usr/lib/u-boot/${MACHINE}" > \
        ${S}/debian/u-boot-${MACHINE}.install
    echo "flash-pg2.bin /usr/lib/u-boot/${MACHINE}" >> \
        ${S}/debian/u-boot-${MACHINE}.install
    echo -$(${ISAR_RELEASE_CMD}) > ${S}/.scmversion
    cp ${WORKDIR}/rules ${S}/debian/rules
    rm -rf ${S}/keys
}

do_prepare_build:append:secureboot() {
    mkdir -p ${S}/keys
    ln -f ${WORKDIR}/keys/* ${S}/keys/
    sed -ni '/### Secure boot config/q;p' ${S}/configs/${U_BOOT_CONFIG}
    cat ${WORKDIR}/secure-boot.cfg >> ${S}/configs/${U_BOOT_CONFIG}
}

dpkg_runbuild:append:secureboot() {
    # remove private keys from source archive
    gunzip ${WORKDIR}/${PN}_${PV}.tar.gz
    tar --delete -f ${WORKDIR}/${PN}_${PV}.tar u-boot-${PV}/keys/custMpk.key u-boot-${PV}/keys/custMpk.pem
    gzip ${WORKDIR}/${PN}_${PV}.tar
}

do_prepare_build:append:otpcmd() {
    ln -sf /usr/lib/secure-boot-otp-provisioning/otpcmd.bin ${S}
    sed -ni '/### OTP command config/q;p' ${S}/configs/${U_BOOT_CONFIG}
    cat ${WORKDIR}/otpcmd.cfg >> ${S}/configs/${U_BOOT_CONFIG}
}

do_prepare_build:append:rpmb-setup() {
    sed -ni '/### RPMB key pairing config/q;p' ${S}/configs/${U_BOOT_CONFIG}
    cat ${WORKDIR}/rpmb-setup.cfg >> ${S}/configs/${U_BOOT_CONFIG}
}

do_deploy() {
    for gen in pg1 pg2; do
        dpkg --fsys-tarfile ${WORKDIR}/u-boot-${MACHINE}_${PV}*.deb | \
            tar xOf - "./usr/lib/u-boot/${MACHINE}/flash-${gen}.bin" \
            > "${DEPLOY_DIR_IMAGE}/iot2050-${gen}-image-boot.bin"
    done
    dpkg --fsys-tarfile ${WORKDIR}/u-boot-${MACHINE}-config_${PV}*.deb | \
        tar xOf - "./etc/${U_BOOT_ENV}" \
        > "${DEPLOY_DIR_IMAGE}/${U_BOOT_ENV}"
}

addtask deploy after do_dpkg_build before do_build
do_deploy[dirs] = "${DEPLOY_DIR_IMAGE}"
