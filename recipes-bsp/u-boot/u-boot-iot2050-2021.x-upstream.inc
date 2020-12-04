#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    git://github.com/siemens/u-boot.git;protocol=https;branch=${U_BOOT_BRANCH};rev=${U_BOOT_BRANCH} \
    "

U_BOOT_BRANCH = "jan/iot2050"
U_BOOT_CONFIG = "iot2050_defconfig"
U_BOOT_BIN = "flash.bin"

SPI_FLASH_IMG = "${U_BOOT_BIN}"
SPI_FLASH_DEPLOY_IMG = "iot2050-image-boot.bin"

DEPENDS += "trusted-firmware-a-iot2050 optee-os-iot2050"
DEBIAN_BUILD_DEPENDS =. "trusted-firmware-a-iot2050, optee-os-iot2050, \
    swig:native, python3-dev:native, python3-pkg-resources,"

do_prepare_build_append() {
    cd ${S}
    ln -sf ../prebuild/* ${S}
}

dpkg_runbuild_prepend() {
    export ATF=/usr/lib/trusted-firmware-a/iot2050/bl31.bin
    export TEE=/usr/lib/optee-os/iot2050/tee-pager_v2.bin
}
