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

require optee-os-iot2050_3.19.0.inc

DEPENDS += "optee-ftpm"
DEBIAN_BUILD_DEPENDS += ", optee-ftpm"

FTPM_UUID="bc50d971-d4c9-42c4-82cb-343fb7f37896"

OPTEE_EXTRA_BUILDARGS += " CFG_EARLY_TA=y EARLY_TA_PATHS=/usr/lib/optee/${FTPM_UUID}.stripped.elf"

python() {
    import re

    overrides = d.getVar('OVERRIDES')
    if re.search("rpmb-setup", overrides):
        if re.search("secureboot", overrides):
            bb.fatal("Not possible to use Secure Boot and RPMB setup for OPTEE")
        if d.getVar('PRODUCT_GENERATION') == "pg1":
            bb.warn("PG1 devices do not supported RPMB based secure storage")
}
