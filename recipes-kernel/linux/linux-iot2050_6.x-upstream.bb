#
# Copyright (c) Siemens AG, 2020-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += " \
    git://github.com/siemens/linux.git;protocol=https;branch=jan/iot2050 \
    file://${KERNEL_DEFCONFIG} \
    file://iot2050_defconfig_extra.cfg \
    "
SRCREV = "${AUTOREV}"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"

S = "${WORKDIR}/git"
