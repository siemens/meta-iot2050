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

SRC_URI += "https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git/snapshot/trusted-firmware-a-lts-v${PV}.tar.gz"
SRC_URI[sha256sum] = "e089b6f91fb205e3a0489d4905e51631b6ce667af6bc4ab0a0143fe2b48b0db8"

S = "${WORKDIR}/trusted-firmware-a-lts-v${PV}"

TF_A_NAME = "iot2050"
TF_A_PLATFORM = "k3"
TF_A_EXTRA_BUILDARGS = "SPD=opteed K3_USART=1"
TF_A_BINARIES = "generic/release/bl31.bin"
