#
# Copyright (c) Siemens AG, 2018-2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

KERNEL_SOURCE = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-${PV}.tar.xz"

SRC_URI[sha256sum] = "19a15e838885a0081de5f9874e608fc3f3b1d9e69f2cc5cfa883b8b5499bcb2e"

S = "${WORKDIR}/linux-${PV}"
