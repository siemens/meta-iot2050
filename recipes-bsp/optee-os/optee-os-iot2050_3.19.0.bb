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

python() {
    import re

    overrides = d.getVar('OVERRIDES')
    if re.search("rpmb-setup", overrides):
        if re.search("secureboot", overrides):
            bb.fatal("Not possible to use Secure Boot and RPMB setup for OPTEE")
        if d.getVar('PRODUCT_GENERATION') == "pg1":
            bb.warn("PG1 devices do not supported RPMB based secure storage")
}
