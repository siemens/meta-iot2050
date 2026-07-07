#
# Copyright (c) Siemens AG, 2022-2026
#
# Authors:
#  Su Baocheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

PR = "1"

SRC_URI += " \
    https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2 \
    file://0001-arm-dts-iot2050-Add-overlay-for-DMA-isolation-for-de.patch \
    file://0002-board-siemens-iot2050-Generalize-overlay_prepare.patch \
    file://0003-board-siemens-iot2050-Allow-to-enable-and-adjust-res.patch \
    file://0004-arm-dts-iot2050-Enforce-DMA-isolation-for-devices-be.patch \
    file://0005-remoteproc-k3-add-config-to-gate-R5F-firmware-authen.patch \
    file://0006-u-boot-iot2050-Add-openssl-provider-support.patch \
    file://0007-dts-k3-am65-iot2050-Switch-to-SHA512-for-FIT-image-p.patch \
    file://0008-tools-iot2050-Switch-to-SHA512-for-signing.patch \
    file://0009-lib-efi_loader-Silence-missing-EFI-var-file-on-first.patch \
    file://0010-tools-fdtgrep-Preserve-padding-in-SPL-control-DTB.patch \
    file://0011-configs-iot2050-Add-padding-for-K3-FDT-fixups.patch \
    file://0012-arm64-dts-ti-iot2050-Keep-SPI-NOR-node-in-SPL.patch \
    file://0013-arm-k3-Fix-SPL-reserved-memory-fixup-order.patch \
    file://0014-arm-armv8-mmu-Match-reserved-memory-basenames.patch \
    "

SRC_URI[sha256sum] = "78e8bfc382fe388f9b55aa1daf8c563522a037779b5d4c349d1415e381f1243e"

S = "${WORKDIR}/u-boot-${PV}"
