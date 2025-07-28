#
# Copyright (c) Siemens AG, 2020-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-bsp/trusted-firmware-a/trusted-firmware-a-custom.inc

SRC_URI += "https://github.com/ARM-software/arm-trusted-firmware/archive/refs/tags/lts-v${PV}.tar.gz"
SRC_URI[sha256sum] = "8fe5e74db3e15d447cb268d4965a46c93a81d1636ee326b5c4ec44cb31c0a2fc"

S = "${WORKDIR}/arm-trusted-firmware-lts-v${PV}"

TF_A_NAME = "iot2050"
TF_A_PLATFORM = "k3"
TF_A_EXTRA_BUILDARGS = "SPD=opteed K3_USART=1"
TF_A_BINARIES = "generic/release/bl31.bin"
