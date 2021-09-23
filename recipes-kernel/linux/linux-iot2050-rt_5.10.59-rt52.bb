#
# Copyright (c) Siemens AG, 2018-2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

KERNEL_BASE_VER = "${@d.getVar('PV').split('-')[0]}"

KERNEL_SOURCE = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-${KERNEL_BASE_VER}.tar.xz"
SRC_URI[sha256sum] = "333cadc15f23e2060bb9701dbd9c23cfb196c528cded797329a0c369c2b6ea80"

SRC_URI += " \
    https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/5.10/older/patch-${PV}.patch.xz;sha256sum=bdf17a434c40f21f69cd60028e36347ebdbad76359e98ae8c6c9de2b6df8c644 \
    file://iot2050-rt.cfg"

S = "${WORKDIR}/linux-${KERNEL_BASE_VER}"
