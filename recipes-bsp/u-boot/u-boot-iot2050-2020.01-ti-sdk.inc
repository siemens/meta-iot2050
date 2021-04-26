#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Chao Zeng <chao.zeng@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    https://git.ti.com/cgit/ti-u-boot/ti-u-boot/snapshot/ti-u-boot-${U_BOOT_REV}.tar.xz; \
    file://2020.01-ti-sdk/0001-arm-dts-Add-IOT2050-device-tree-files.patch \
    file://2020.01-ti-sdk/0002-board-siemens-Add-support-for-SIMATIC-IOT2050-device.patch \
    file://2020.01-ti-sdk/0003-Add-the-function-convert-string-to-upper.patch \
    file://2020.01-ti-sdk/0004-Remove-Binman-Use-its-to-generate-u-boot.patch \
    file://2020.01-ti-sdk/0005-mtd-spi-Add-support-of-flash-protection-to-w25q128.patch \
    file://2020.01-ti-sdk/0006-board-add-the-defconfig-to-support-flash-protect-and.patch \
    file://2020.01-ti-sdk/iot2050-uboot-ti-sdk-rules \
    "

U_BOOT_REV = "3c9ebdb87d65aacc4ec302be8bef3df15364bacd"
U_BOOT_CONFIG = "iot2050_defconfig"
U_BOOT_BIN = "flash.bin"
SRC_URI[sha256sum] = "de74533e31636c4491944329508144149e132d4d35e6c0ca8c394b8d69ac9e73"
S = "${WORKDIR}/ti-u-boot-${U_BOOT_REV}"

SPI_FLASH_IMG = "${U_BOOT_BIN}"
SPI_FLASH_DEPLOY_IMG = "iot2050-image-boot.bin"

DEPENDS += "trusted-firmware-a-iot2050 optee-os-iot2050"
DEBIAN_BUILD_DEPENDS =. "trusted-firmware-a-iot2050, optee-os-iot2050, \
    swig:native, python3-dev:native, python3-pkg-resources,python-dev:native,"

dpkg_runbuild_prepend() {
    export ATF=/usr/lib/trusted-firmware-a/iot2050/bl31.bin
    export TEE=/usr/lib/optee-os/iot2050/tee-pager_v2.bin
    export IOT2050_VARIANT=${IOT2050_VARIANT}
    export SPI_FLASH_IMG=${SPI_FLASH_IMG}
    export SPI_FLASH_SIZE_KB=${SPI_FLASH_SIZE_KB}
}

do_prepare_build_append() {
    cp ${WORKDIR}/2020.01-ti-sdk/iot2050-uboot-ti-sdk-rules ${S}/debian/rules
}
