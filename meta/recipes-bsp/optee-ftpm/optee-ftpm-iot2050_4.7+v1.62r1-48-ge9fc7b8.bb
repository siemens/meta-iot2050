# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
#

PR="1"

require recipes-bsp/optee-ftpm/optee-ftpm.inc

SRC_URI += " \
    https://github.com/OP-TEE/optee_ftpm/archive/${SRCREV}.tar.gz;downloadfilename=optee_ftpm-${SRCREV}.tar.gz \
    https://github.com/microsoft/ms-tpm-20-ref/archive/${SRCREV_ms-tpm}.tar.gz;name=ms-tpm;downloadfilename=ms-tpm-20-ref-${SRCREV_ms-tpm}.tar.gz \
    file://0001-fTPM-use-TA_FLAG_DEVICE_ENUM_SUPP-for-kernels-withou.patch \
    "
SRCREV = "ce33372ab772e879826361a1ca91126260bd9be1"
SRCREV_ms-tpm = "e9fc7b89d865536c46deb63f9c7d0121a3ded49c"

SRC_URI[sha256sum] = "edeb2a1bcf39d80a2e0abb11ba7026af48efd748009ae1f5ab674c1288ff04cb"
SRC_URI[ms-tpm.sha256sum] = "b77d092c0dde362adf6bc88a580ca7c8abe124d69bb734bf28f8904ae30494a4"

S = "${WORKDIR}/optee_ftpm-${SRCREV}"
MS_TPM_20_REF_DIR = "ms-tpm-20-ref-${SRCREV_ms-tpm}"

OPTEE_NAME = "iot2050"
TA_CPU = "cortex-a53"
TA_DEV_KIT_DIR = "/usr/lib/optee-os/${OPTEE_NAME}/export-ta_arm64"
