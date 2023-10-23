#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
#

require recipes-bsp/optee-client/optee-client-custom.inc

SRC_URI += "https://github.com/OP-TEE/optee_client/archive/${PV}.tar.gz;downloadfilename=optee_client-${PV}.tar.gz"
SRC_URI[sha256sum] = "bcdac9c3a9f2e93c64d114667cc6d1feddf9f978992cdc2d59745885f9bd8fbe"

S = "${WORKDIR}/optee_client-${PV}"
