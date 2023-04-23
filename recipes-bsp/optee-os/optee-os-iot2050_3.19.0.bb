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
require recipes-bsp/optee-os/optee-os-custom.inc
require optee-os-iot2050_3.19.0.inc

# StMM integration
DEPENDS += "edk2-standalonemm-rpmb"
DEBIAN_BUILD_DEPENDS += ", edk2-standalonemm-rpmb"
OPTEE_EXTRA_BUILDARGS += " \
    CFG_STMM_PATH=/usr/lib/edk2/BL32_AP_MM.fd \
    "

# RPMB key pairing
OPTEE_EXTRA_BUILDARGS:append:rpmb-setup = " CFG_RPMB_WRITE_KEY=y"

python() {
    import re

    overrides = d.getVar('OVERRIDES')
    if re.search("rpmb-setup", overrides):
        if re.search("secureboot", overrides):
            bb.fatal("Not possible to use Secure Boot and RPMB setup for OPTEE")
        if d.getVar('PRODUCT_GENERATION') == "pg1":
            bb.warn("PG1 devices do not supported RPMB based secure storage")
}
