#
# Copyright (c) Siemens AG, 2022-2025
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
    "

SRC_URI[sha256sum] = "439d3bef296effd54130be6a731c5b118be7fddd7fcc663ccbc5fb18294d8718"

S = "${WORKDIR}/u-boot-${PV}"
