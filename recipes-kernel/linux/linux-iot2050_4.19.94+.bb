#
# Copyright (c) Siemens AG, 2018
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += "https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/snapshot/ti-linux-kernel-${KERNEL_REV}.tar.xz"

SRC_URI += "file://${KERNEL_DEFCONFIG}"
SRC_URI += "file://${KERNEL_DEFCONFIG_EXTRA}"

SRC_URI += " \
    file://0001-iot2050-add-iot2050-platform-support.patch \
    file://0002-Add-support-for-U9300C-TD-LTE-module.patch \
    file://0003-feat-Add-CP210x-driver-support-to-software-flow-cont.patch \
    file://0004-fix-disable-usb-lpm-to-fix-usb-device-reset.patch \
    file://0005-Fix-DP-maybe-not-display-problem.patch \
    file://0006-fix-fix-the-hardware-flow-function-of-cp2102n24.patch \
    file://0007-feat-add-io-expander-pcal9535-support.patch \
    file://0008-setting-the-RJ45-port-led-behavior.patch \
    file://0009-fix-clear-the-cycle-buffer-of-serial.patch \
    file://0010-feat-extend-led-panic-indicator-on-and-off.patch \
    file://0011-fix-can-not-auto-negotiate-to-100M-with-4-wire.patch \
    file://0012-feat-change-mmc-order-using-alias-in-dts.patch \
    file://0013-fix-PLL4_DCO-freq-over-range-cause-DP-not-display.patch"

KERNEL_BRANCH = "am6-abi-ti-linux-4.19.y"
KERNEL_REV = "c7a3b610edfb5a0ee0313e1432bf328362269d05"
SRC_URI[sha256sum] = "33871edb3bee5ed5491f63700ec37eda9430e20f7825af8a55f7d0799bcd64ea"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"
KERNEL_DEFCONFIG_EXTRA = "iot2050_defconfig_extra.cfg"

S = "${WORKDIR}/ti-linux-kernel-${KERNEL_REV}"
