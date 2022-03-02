#
# Copyright (c) Siemens AG, 2019-2020
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
    file://keys \
    file://prebuild \
    file://fw_env.config"

U_BOOT_BIN = "flash.bin"

SPI_FLASH_IMG = "${U_BOOT_BIN}"
SPI_FLASH_DEPLOY_IMG ??= "iot2050-image-boot.bin"

# Needed to resolve races as long as the layer has to rebuild swig
DEPENDS += "swig"

# Build environment
DEPENDS += "trusted-firmware-a-iot2050 optee-os-iot2050 k3-rti-wdt"
DEBIAN_BUILD_DEPENDS =. "openssl, libssl-dev:native, libssl-dev:arm64, \
    trusted-firmware-a-iot2050, optee-os-iot2050, k3-rti-wdt, \
    swig, python3-dev:native, python3-pkg-resources,"

U_BOOT_CONFIG_PACKAGE = "1"

do_prepare_build_append() {
    cd ${S}
    ln -sf ../prebuild/* ${S}
    ln -sf ../keys ${S}
    ln -sf /lib/firmware/k3-rti-wdt.fw ${S}
    echo "${SPI_FLASH_IMG} /usr/lib/u-boot/${MACHINE}" > \
        ${S}/debian/u-boot-${MACHINE}.install
    echo -$(${ISAR_RELEASE_CMD}) > ${S}/.scmversion
}

dpkg_runbuild_prepend() {
    export ATF=/usr/lib/trusted-firmware-a/iot2050/bl31.bin
    export TEE=/usr/lib/optee-os/iot2050/tee-pager_v2.bin
}

dpkg_build_sstate_prepare_append() {
    ln -f ${S}/${SPI_FLASH_IMG} -t ${DPKG_SSTATE}
}

dpkg_build_sstate_finalize_append() {
    ln -f ${DPKG_SSTATE}/${SPI_FLASH_IMG} -t ${S}
}

do_deploy() {
    cp -f "${S}/${SPI_FLASH_IMG}" "${DEPLOY_DIR_IMAGE}/${SPI_FLASH_DEPLOY_IMG}"
}

addtask deploy after do_dpkg_build before do_build
do_deploy[dirs] = "${DEPLOY_DIR_IMAGE}"
