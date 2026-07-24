#
# Copyright (c) Siemens AG, 2020-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

SRC_URI += "https://github.com/OP-TEE/optee_os/archive/${PV}.tar.gz;downloadfilename=optee-os-${PV}.tar.gz \
           file://0001-plat-k3-main-Provide-plat_rng_init-stub.patch \
           "
SRC_URI[sha256sum] = "18633691cb075ff2249422251f1cd77c30439a95b564b46682dea1fb6580a5af"

S = "${WORKDIR}/optee_os-${PV}"

DEBIAN_BUILD_DEPENDS += ", python3-cryptography:native"

OPTEE_NAME = "iot2050"
OPTEE_PLATFORM = "k3-am65x"
OPTEE_EXTRA_BUILDARGS = " \
    TEE_IMPL_VERSION=${PV} \
    CFG_ARM64_core=y CFG_TEE_CORE_LOG_LEVEL=2 CFG_USER_TA_TARGETS=ta_arm64 \
    CFG_CONSOLE_UART=1 CFG_CORE_DYN_SHM=y \
    CFG_WITH_SOFTWARE_PRNG=n \
    CFG_HWRNG_PTA=y CFG_HWRNG_QUALITY=1024 \
    CFG_INSECURE=n \
    CFG_REE_FS=n CFG_CORE_HEAP_SIZE=524288 \
    "

OPTEE_COMMON_RPMB_CFG = "CFG_RPMB_FS=y CFG_RPMB_FS_DEV_ID=1"

OPTEE_EXTRA_BUILDARGS:append:rpmb-setup = " \
    ${OPTEE_COMMON_RPMB_CFG} \
    "

OPTEE_EXTRA_BUILDARGS:append:secureboot = " \
    ${OPTEE_COMMON_RPMB_CFG} \
    "
