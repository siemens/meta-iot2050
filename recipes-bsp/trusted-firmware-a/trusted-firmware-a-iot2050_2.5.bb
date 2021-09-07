#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-bsp/trusted-firmware-a/trusted-firmware-a-custom.inc

SRC_URI += "https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git/snapshot/trusted-firmware-a-${PV}.tar.gz"
SRC_URI[sha256sum] = "ad8a2ffcbcd12d919723da07630fc0840c3c2fba7656d1462e45488e42995d7c"

S = "${WORKDIR}/trusted-firmware-a-${PV}"

TF_A_NAME = "iot2050"
TF_A_PLATFORM = "k3"
TF_A_EXTRA_BUILDARGS = "SPD=opteed K3_USART=1"
TF_A_BINARIES = "generic/release/bl31.bin"
