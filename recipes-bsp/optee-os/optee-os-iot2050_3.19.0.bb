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
SRC_URI[sha256sum] = "5e0c03bbc4d106f262a6bd33333c002c3380205ae6b82334aa7b644721ff7868"

S = "${WORKDIR}/optee_os-${PV}"

DEBIAN_BUILD_DEPENDS += ", python3-cryptography:native"

OPTEE_NAME = "iot2050"

OPTEE_PLATFORM = "k3-am65x"
OPTEE_EXTRA_BUILDARGS = " \
    TEE_IMPL_VERSION=${PV} \
    CFG_ARM64_core=y CFG_TEE_CORE_LOG_LEVEL=2 CFG_USER_TA_TARGETS=ta_arm64 \
    CFG_CONSOLE_UART=1 CFG_RPMB_FS=y CFG_RPMB_FS_DEV_ID=1 CFG_CORE_DYN_SHM=y \
    CFG_IN_TREE_EARLY_TAS=avb/023f8f1a-292a-432b-8fc4-de8471358067 \
    CFG_WARN_INSECURE=n"

OPTEE_EXTRA_BUILDARGS_append_rpmb-setup = " CFG_RPMB_WRITE_KEY=y"

python() {
    import re

    overrides = d.getVar('OVERRIDES')
    if re.search("rpmb-setup", overrides) and re.search("secureboot", overrides):
        bb.fatal("Not possible to use Secure Boot and RPMB setup for OPTEE")
}
