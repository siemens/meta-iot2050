#
# Copyright (c) Siemens AG, 2018-2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

KERNEL_BASE_VER = "${@d.getVar('PV').split('-')[0]}"

KERNEL_SOURCE = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-${KERNEL_BASE_VER}.tar.xz"

SRC_URI[sha256sum] = "edd3dedbce5bcaa5ba7cde62f8f3fd58b2ab21e2ec427b9d200685da5ec03e66"

SRC_URI += " \
    https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/5.10/older/patch-${PV}.patch.xz;sha256sum=a355068c2802a52705f00c0a61afc73ced4ecb8d712976fa80ac9584068bbeeb \
    file://iot2050-rt.cfg"

S = "${WORKDIR}/linux-${KERNEL_BASE_VER}"
