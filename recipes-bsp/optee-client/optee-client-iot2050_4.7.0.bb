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
SRC_URI[sha256sum] = "e6c6b93e2be417df57ceb05a2eb6505744e3fbdd3b2ae5e5bf79bf6028b6f84d"

S = "${WORKDIR}/optee_client-${PV}"
