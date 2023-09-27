#
# Copyright (c) Siemens AG, 2022-2023
#
# Authors:
#  Su Baocheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2 \
    file://0001-Watchdog-Support-WDIOF_CARDRESET-on-TI-AM65x-platfor.patch \
    file://0002-tools-iot2050-sign-fw.sh-Make-localization-of-tools-.patch \
    file://0003-board-siemens-iot2050-Fix-logical-bug-in-PG1-PG2-det.patch \
    "

SRC_URI[sha256sum] = "e00e6c6f014e046101739d08d06f328811cebcf5ae101348f409cbbd55ce6900"

S = "${WORKDIR}/u-boot-${PV}"
