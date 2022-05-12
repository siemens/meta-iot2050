#
# Copyright (c) Siemens AG, 2020-2022
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Su Baocheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2 \
    file://0001-iot2050-binman-add-missing-msg-for-blobs.patch \
    file://0002-watchdog-rti_wdt-Add-10-safety-margin-to-clock-frequ.patch \
    file://0003-mtd-spi-Convert-is_locked-callback-to-is_unlocked.patch \
    file://0004-sf-Query-write-protection-status-before-operating-th.patch \
    file://0005-arm-dts-iot2050-Add-cfg-register-space-for-ringacc-a.patch \
    file://0006-board-siemens-iot2050-Split-the-build-for-PG1-and-PG.patch \
    file://0007-arm-dts-iot2050-Use-the-auto-generator-nodes-for-fdt.patch \
    file://0008-iot2050-Update-firmware-layout.patch \
    file://0009-lib-crypto-Enable-more-algorithms-in-cert-verificati.patch \
    file://0010-efi_loader-use-pUs-for-printing-GUIDs.patch \
    file://0011-efi_loader-correctly-handle-mixed-hashes-and-signatu.patch \
    file://0012-efi_loader-Improve-console-screen-clearing-and-reset.patch \
    file://0013-env-Complete-generic-support-for-writable-list.patch \
    file://0014-env-Couple-networking-related-variable-flags-to-CONF.patch \
    file://0015-introduce-CONFIG_DEVICE_TREE_INCLUDES.patch \
    file://0016-tools-Add-script-for-converting-public-key-into-devi.patch \
    file://0017-binman-Include-also-subnodes-in-generator-nodes.patch \
    file://0018-image-fit-Make-string-of-algo-parameter-constant.patch \
    file://0019-mkimage-Allow-to-specify-the-signature-algorithm-on-.patch \
    file://0020-iot2050-Add-watchdog-start-to-bootcmd.patch \
    file://0021-iot2050-Add-CONFIG_ENV_FLAGS_LIST_STATIC.patch \
    file://0022-arm-dts-iot2050-Allow-verifying-U-Boot-proper-by-SPL.patch \
    file://0023-iot2050-Add-script-for-signing-artifacts.patch \
    file://0024-arm-dts-iot2050-Optionally-embed-OTP-programming-dat.patch \
    "

SRC_URI[sha256sum] = "81b4543227db228c03f8a1bf5ddbc813b0bb8f6555ce46064ef721a6fc680413"

S = "${WORKDIR}/u-boot-${PV}"
