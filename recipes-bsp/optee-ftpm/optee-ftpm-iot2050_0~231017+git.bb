# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
#
require recipes-bsp/optee-ftpm/optee-ftpm.inc

SRC_URI += " \
    https://github.com/Microsoft/ms-tpm-20-ref/archive/${SRCREV}.tar.gz \
    https://github.com/wolfSSL/wolfssl/archive/${SRCREV-wolfssl}.tar.gz;name=wolfssl \
    file://0001-add-enum-to-ta-flags.patch \
    "

SRCREV = "e9fc7b89d865536c46deb63f9c7d0121a3ded49c"
SRCREV-wolfssl = "9db828a099bda150a4595cf89954c15877947039"

SRC_URI[sha256sum] = "b77d092c0dde362adf6bc88a580ca7c8abe124d69bb734bf28f8904ae30494a4"
SRC_URI[wolfssl.sha256sum] = "18f77959daf2a7995757cc7e6c86efe513aa6e355e4770bba6d36bf677fe88df"

S = "${WORKDIR}/ms-tpm-20-ref-${SRCREV}"

OPTEE_NAME = "iot2050"
TA_CPU = "cortex-a53"
TA_DEV_KIT_DIR = "/usr/lib/optee-os/${OPTEE_NAME}/export-ta_arm64"

do_prepare_build:append() {
    rm -rf ${S}/external/wolfssl
    cp -a ${S}/../wolfssl-${SRCREV-wolfssl} ${S}/external/wolfssl
}
