#
# Copyright (c) Siemens AG, 2018-2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

KERNEL_SOURCE = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-${PV}.tar.xz"

SRC_URI[sha256sum] = "edd3dedbce5bcaa5ba7cde62f8f3fd58b2ab21e2ec427b9d200685da5ec03e66"

S = "${WORKDIR}/linux-${PV}"
