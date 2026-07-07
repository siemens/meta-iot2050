#
# Copyright (c) Siemens AG, 2023-2026
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#

inherit optee-client

SRC_URI += "https://github.com/OP-TEE/optee_client/archive/${PV}.tar.gz;downloadfilename=optee_client-${PV}.tar.gz"
SRC_URI[sha256sum] = "984084a465f55ed8037e0e27eb4399149b5cec981ed295c2f0ee0dd515f60af9"

S = "${WORKDIR}/optee_client-${PV}"
