#
# Copyright (c) Siemens AG, 2018
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += "https://git.ti.com/cgit/processor-sdk/processor-sdk-linux/snapshot/processor-sdk-linux-${KERNEL_REV}.tar.xz"

SRC_URI += "file://${KERNEL_DEFCONFIG}"
SRC_URI += "file://${KERNEL_DEFCONFIG_EXTRA}"

SRC_URI += "file://0001-iot2050-add-iot2050-platform-support.patch \
    file://0002-Add-support-for-U9300C-TD-LTE-module.patch \
    file://0003-feat-Add-CP210x-driver-support-to-software-flow-cont.patch \
    file://0004-fix-disable-usb-lpm-to-fix-usb-device-reset.patch \
    file://0005-Fix-DP-maybe-not-display-problem.patch \
    file://0006-fix-fix-the-hardware-flow-function-of-cp2102n24.patch \
    file://0007-serial-8250-8250_omap-Fix-DMA-teardown-sequence-duri.patch \
    file://0008-serial-8250-8250_omap-Remove-redundant-call-to-omap_.patch \
    file://0009-feat-add-io-expander-pcal9535-support.patch \
    file://0010-feat-modify-kernel-to-load-fw-from-MTD-for-pru-rtu.patch \
    file://0011-setting-the-RJ45-port-led-behavior.patch \
    file://0012-fix-clear-the-cycle-buffer-of-serial.patch \
    file://0013-fix-4169461-fixed-eth-link-down-when-autoneg-off.patch \
    file://0014-refactor-move-ioexpander-node-to-mcu-i2c0-for-LM5.patch \
    file://0015-fix-rproc-r5-0-set_config-failed-in-linux.patch \
    file://0016-feat-extend-led-panic-indicator-on-and-off.patch \
    file://0017-fix-can-not-auto-negotiate-to-100M-with-4-wire.patch \
    file://0018-change-OSPI-clock-id-to-support-sysfw-19.12.patch \
    file://0019-feat-set-sdhci0-clock-frequency-to-142.86MHz.patch \
    file://0020-feat-change-mmc-order-using-alias-in-dts.patch \
    file://0021-fix-PLL4_DCO-freq-over-range-cause-DP-not-display.patch \
    file://0022-iot2050-Provide-dtb-for-devices-using-boot-load-V01..patch"

KERNEL_REV = "5f8c1c6121da785bbe7ecc5896877a2537b5d6eb"
SRC_URI[sha256sum] = "ef031959fd8242b943d0aa54ad4bf6338b698577739867701f6d7c7d04ec6e1f"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"
KERNEL_DEFCONFIG_EXTRA = "iot2050_defconfig_extra.cfg"

S = "${WORKDIR}/processor-sdk-linux-${KERNEL_REV}"
