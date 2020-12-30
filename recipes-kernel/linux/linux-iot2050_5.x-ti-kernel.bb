#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += " \
    https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/snapshot/ti-linux-kernel-${KERNEL_REV}.tar.xz;protocol=https; \
    file://ti-kernel/0001-iot2050-add-iot2050-platform-support.patch \
    file://ti-kernel/0002-Add-support-for-U9300C-TD-LTE-module.patch \
    file://ti-kernel/0003-feat-Add-CP210x-driver-support-to-software-flow-cont.patch \
    file://ti-kernel/0004-fix-disable-usb-lpm-to-fix-usb-device-reset.patch \
    file://ti-kernel/0005-setting-the-RJ45-port-led-behavior.patch \
    file://ti-kernel/0006-refactor-move-ioexpander-node-to-mcu-i2c0-for-LM5.patch \
    file://ti-kernel/0007-feat-extend-led-panic-indicator-on-and-off.patch \
    file://ti-kernel/0008-feat-change-mmc-order-using-alias-in-dts.patch"

SRC_URI += " \
    file://${KERNEL_DEFCONFIG} \
    file://iot2050-upstream.cfg \
    file://iot2050_defconfig_extra.cfg"

KERNEL_REV = "07.01.00.006"
KERNEL_DEFCONFIG = "iot2050_defconfig_base"
SRC_URI[sha256sum] = "dd446c42889866ec863334e7995dd391564e0e5a6b132c65d22394466c814b96"

S = "${WORKDIR}/ti-linux-kernel-${KERNEL_REV}"
