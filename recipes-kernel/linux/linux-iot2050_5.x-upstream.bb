#
# Copyright (c) Siemens AG, 2020-2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += " \
    git://github.com/siemens/linux.git;protocol=https;branch=${KERNEL_BRANCH};rev=${KERNEL_BRANCH} \
    file://${KERNEL_DEFCONFIG} \
    file://iot2050_defconfig_extra.cfg \
    "

KERNEL_BRANCH = "jan/iot2050"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"

S = "${WORKDIR}/git"
