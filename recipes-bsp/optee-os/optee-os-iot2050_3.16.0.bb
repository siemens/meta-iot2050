#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-bsp/optee-os/optee-os-custom.inc

SRC_URI += "https://github.com/OP-TEE/optee_os/archive/${PV}.tar.gz"
SRC_URI[sha256sum] = "ebc8e18ad2039ee97c34f74a7546de9119e26f04c368b6c7fd0c55f93d33d2d6"

S = "${WORKDIR}/optee_os-${PV}"

DEBIAN_BUILD_DEPENDS += ", python3-cryptography:native"

OPTEE_NAME = "iot2050"

OPTEE_PLATFORM = "k3-am65x"
OPTEE_EXTRA_BUILDARGS = " \
    CFG_ARM64_core=y CFG_TEE_CORE_LOG_LEVEL=2 CFG_USER_TA_TARGETS=ta_arm64 \
    CFG_CONSOLE_UART=1"

dpkg_runbuild_prepend() {
    export TEE_IMPL_VERSION=${PV}
}
