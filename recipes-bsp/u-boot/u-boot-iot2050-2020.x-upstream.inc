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
U_BOOT_BIN = "flash.bin"
U_BOOT_RULES = "iot2050-uboot-rules"

SPI_FLASH_IMG = "${U_BOOT_BIN}"
SPI_FLASH_DEPLOY_IMG = "iot2050-image-boot.bin"

DEPENDS += "arm-trusted-firmware-iot2050 op-tee-iot2050"
DEBIAN_BUILD_DEPENDS =. "arm-trusted-firmware-iot2050, op-tee-iot2050,"
