#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Su Baocheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050_2021.04.inc

SPI_FLASH_DEPLOY_IMG = "iot2050-pg2-image-boot.bin"

do_prepare_build_append() {
    ln -sf ../prebuild/tiboot3_sr2.bin ${S}/tiboot3.bin
}
