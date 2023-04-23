# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
#
inherit dpkg

SUMMARY = "OPTEE fTPM Microsoft TA"
DESCRIPTION = "TCG reference implementation of the TPM 2.0 Specification."
HOMEPAGE = "https://github.com/microsoft/ms-tpm-20-ref/"

FTPM_UUID="bc50d971-d4c9-42c4-82cb-343fb7f37896"

SRC_URI = " \
    https://github.com/Microsoft/ms-tpm-20-ref/archive/${SRCREV}.tar.gz \
    https://github.com/wolfSSL/wolfssl/archive/${SRCREV-wolfssl}.tar.gz;name=wolfssl \
    file://0001-add-enum-to-ta-flags.patch \
    file://rules.tmpl"

SRCREV = "f74c0d9686625c02b0fdd5b2bbe792a22aa96cb6"
# according to ms-tpm-20-ref submodules
SRCREV-wolfssl = "9c87f979a7f1d3a6d786b260653d566c1d31a1c4"

SRC_URI[sha256sum] = "16fabc6ad6cc700d947dbc96efc30ff8ae97e577944466f08193bb37bc1eb64d"
SRC_URI[wolfssl.sha256sum] = "a68c301fa0ee6197158912d808c4258605a2d001e458fd958257cafba17bfd14"

S = "${WORKDIR}/ms-tpm-20-ref-${SRCREV}"

DEPENDS += "optee-os-tadevkit"
DEBIAN_BUILD_DEPENDS = "optee-os-tadevkit, python3-cryptography:native,"

OPTEE_FTPM_BUILD_ARGS = " \
    TA_CPU=cortex-a53 \
    TA_CROSS_COMPILE=${CROSS_COMPILE} \
	CFG_FTPM_USE_WOLF=y \
	TA_DEV_KIT_DIR=/usr/lib/optee-os/export-ta_arm64 \
	CFG_TEE_TA_LOG_LEVEL=2 \
    "

TEMPLATE_FILES = "rules.tmpl"
TEMPLATE_VARS += "OPTEE_FTPM_BUILD_ARGS"

do_prepare_build() {
    deb_debianize

    rm -rf ${S}/external/wolfssl
    cp -a ${S}/../wolfssl-${SRCREV-wolfssl} ${S}/external/wolfssl

    echo "Samples/ARM32-FirmwareTPM/optee_ta/out/fTPM/${FTPM_UUID}.ta /usr/lib/optee/" > \
        ${S}/debian/optee-ftpm.install
    echo "Samples/ARM32-FirmwareTPM/optee_ta/out/fTPM/${FTPM_UUID}.stripped.elf /usr/lib/optee/" >> \
        ${S}/debian/optee-ftpm.install
}
