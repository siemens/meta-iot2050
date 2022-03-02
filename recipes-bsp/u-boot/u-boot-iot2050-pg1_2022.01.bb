#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Su Baocheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050_2022.01.inc

U_BOOT_CONFIG = "iot2050_${PRODUCT_GENERATION}_defconfig"

SPI_FLASH_DEPLOY_IMG = "iot2050-${PRODUCT_GENERATION}-image-boot.bin"
