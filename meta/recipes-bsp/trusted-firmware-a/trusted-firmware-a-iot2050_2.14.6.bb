#
# Copyright (c) Siemens AG, 2020-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit trusted-firmware-a

SRC_URI += "https://github.com/ARM-software/arm-trusted-firmware/archive/refs/tags/lts-v${PV}.tar.gz"
SRC_URI[sha256sum] = "bb15ce95447a987ca8acbaa45126a338671da3c330c41283e3ded969ff1501f2"

S = "${WORKDIR}/arm-trusted-firmware-lts-v${PV}"

TF_A_NAME = "iot2050"
TF_A_PLATFORM = "k3"
# Keep the IOT2050 UART selection and avoid non-reproducible date/time macros.
TF_A_EXTRA_BUILDARGS = "SPD=opteed K3_USART=1 TARGET_BOARD=generic \
	BUILD_MESSAGE_TIMESTAMP='"reproducible"'"
TF_A_BINARIES = "generic/release/bl31.bin"