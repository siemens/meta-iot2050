#
# Copyright (c) Siemens AG, 2020-2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    git://github.com/siemens/u-boot.git;protocol=https;branch=${UBOOT_BRANCH};rev=${UBOOT_BRANCH} \
    "

UBOOT_BRANCH = "jan/iot2050"

S = "${WORKDIR}/git"
