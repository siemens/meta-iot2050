#
# Copyright (c) Siemens AG, 2018
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += "git://git.ti.com/ti-linux-kernel/ti-linux-kernel.git;branch=${KERNEL_BRANCH};rev=${KERNEL_BRANCH}"

SRC_URI += "file://${KERNEL_DEFCONFIG}"
SRC_URI += "file://${KERNEL_DEFCONFIG_EXTRA}"

SRC_URI += "file://0001-iot2050-add-iot2050-platform-support.patch \
    file://0002-Add-support-for-U9300C-TD-LTE-module.patch \
    file://0003-feat-Add-CP210x-driver-support-to-software-flow-cont.patch \
    file://0004-fix-disable-usb-lpm-to-fix-usb-device-reset.patch \
    file://0005-Fix-DP-maybe-not-display-problem.patch \
    file://0006-fix-fix-the-hardware-flow-function-of-cp2102n24.patch \
    file://0007-feat-add-io-expander-pcal9535-support.patch \
    file://0008-setting-the-RJ45-port-led-behavior.patch \
    file://0009-fix-clear-the-cycle-buffer-of-serial.patch \
    file://0010-refactor-move-ioexpander-node-to-mcu-i2c0-for-LM5.patch \
    file://0011-feat-extend-led-panic-indicator-on-and-off.patch \
    file://0012-fix-can-not-auto-negotiate-to-100M-with-4-wire.patch \
    file://0013-dts-Set-sdhci0-clock-frequency-to-142.86MHz.patch \
    file://0014-feat-change-mmc-order-using-alias-in-dts.patch \
    file://0015-fix-PLL4_DCO-freq-over-range-cause-DP-not-display.patch \
    file://0016-iot2050-Provide-dtb-for-devices-using-boot-load-V01..patch \
    file://0017-add-the-sysfw-ABI3.X-support.patch"

KERNEL_BRANCH = "am6-abi-ti-linux-4.19.y"
KERNEL_REV = "c7a3b610edfb5a0ee0313e1432bf328362269d05"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"
KERNEL_DEFCONFIG_EXTRA = "iot2050_defconfig_extra.cfg"

S = "${WORKDIR}/git"
