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
    file://0001-tools-iot2050-sign-fw.sh-Make-localization-of-tools-.patch \
    file://0002-board-siemens-iot2050-Fix-logical-bug-in-PG1-PG2-det.patch \
    file://0003-board-siemens-iot2050-Fix-M.2-detection.patch \
    file://0004-iot2050-Allow-for-more-than-1-USB-storage-device.patch \
    file://0005-board-siemens-iot2050-Fix-coding-style.patch \
    file://0006-board-siemens-iot2050-Control-pcie-power-for-all-var.patch \
    file://0007-board-siemens-iot2050-Pass-DDR-size-from-FSBL.patch \
    file://0008-board-siemens-iot2050-Generalize-the-fdt-fixup.patch \
    file://0009-dts-iot2050-Sync-kernel-dts-to-u-boot.patch \
    file://0010-dts-iot2050-Support-new-IOT2050-SM-variant.patch \
    file://0011-arm-dts-iot2050-Disable-lock-step-mode-for-all-iot20.patch \
    file://0012-spi-cadence-quadspi-Fix-error-message-on-stuck-busy-.patch \
    file://0013-spi-cadence-quadspi-fix-potential-malfunction-after-.patch \
    file://0014-mmc-Fix-potential-timer-value-truncation.patch \
    file://0015-arm-dts-iot2050-Add-overlay-for-DMA-isolation-for-de.patch \
    file://0016-board-siemens-iot2050-Generalize-overlay_prepare.patch \
    file://0017-board-siemens-iot2050-Allow-to-enable-and-adjust-res.patch \
    "

SRC_URI[sha256sum] = "e00e6c6f014e046101739d08d06f328811cebcf5ae101348f409cbbd55ce6900"

S = "${WORKDIR}/u-boot-${PV}"
