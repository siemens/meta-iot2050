#
# Copyright (c) Siemens AG, 2020-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

SRC_URI += "https://github.com/OP-TEE/optee_os/archive/${PV}.tar.gz;downloadfilename=${PN}-${PV}.tar.gz"
SRC_URI[sha256sum] = "92a16e841b0bdb4bfcb1c20b6a1bd3309092203d534ed167dfdb5a5f395bf60b"

S = "${WORKDIR}/optee_os-${PV}"

DEBIAN_BUILD_DEPENDS += ", python3-cryptography:native"

OPTEE_NAME = "iot2050"
OPTEE_PLATFORM = "k3-am65x"
OPTEE_EXTRA_BUILDARGS = " \
    TEE_IMPL_VERSION=${PV} \
    CFG_ARM64_core=y CFG_TEE_CORE_LOG_LEVEL=2 CFG_USER_TA_TARGETS=ta_arm64 \
    CFG_CONSOLE_UART=1 CFG_CORE_DYN_SHM=y \
    CFG_WARN_INSECURE=n \
    CFG_REE_FS=n CFG_CORE_HEAP_SIZE=524288 \
    "

OPTEE_COMMON_RPMB_CFG = "CFG_RPMB_FS=y CFG_RPMB_FS_DEV_ID=1"

OPTEE_EXTRA_BUILDARGS:append:rpmb-setup = " \
    ${OPTEE_COMMON_RPMB_CFG} \
    "

OPTEE_EXTRA_BUILDARGS:append:secureboot = " \
    ${OPTEE_COMMON_RPMB_CFG} \
    "
