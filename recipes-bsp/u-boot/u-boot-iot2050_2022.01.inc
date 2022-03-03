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
    "

SRC_URI[sha256sum] = "81b4543227db228c03f8a1bf5ddbc813b0bb8f6555ce46064ef721a6fc680413"

S = "${WORKDIR}/u-boot-${PV}"
