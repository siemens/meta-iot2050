#
# Copyright (c) Siemens AG, 2018-2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

KERNEL_SOURCE = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-${PV}.tar.xz"

SRC_URI[sha256sum] = "3eb84bd24a2de2b4749314e34597c02401c5d6831b055ed5224adb405c35e30a"

S = "${WORKDIR}/linux-${PV}"
