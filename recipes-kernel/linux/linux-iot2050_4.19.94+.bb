#
# Copyright (c) Siemens AG, 2018-2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += "https://git.ti.com/cgit/processor-sdk/processor-sdk-linux/snapshot/processor-sdk-linux-${KERNEL_REV}.tar.xz"

SRC_URI += "file://${KERNEL_DEFCONFIG}"
SRC_URI += "file://${KERNEL_DEFCONFIG_EXTRA}"

SRC_URI += " \
    file://0001-firmware-ti_sci-Add-support-for-getting-resource-wit.patch \
    file://0002-firmware-ti_sci-Rework-the-irq_ops-to-configure-inta.patch \
    file://0003-firmware-ti_sci-Use-dev_id-as-resource-type-with-ABI.patch \
    file://0004-irqchip-ti-sci-inta-Add-ABI-3.0-support.patch \
    file://0005-irqchip-ti-sci-intr-Add-ABI-3.0-support.patch \
    file://0006-HACK-dma-am65x-Update-rchan-oes-offset-with-ABI-3.0.patch \
    file://0007-arm64-dts-ti-k3-am654-Introduce-ABI3.x-specific-dts.patch \
    file://0008-iot2050-add-iot2050-platform-support.patch \
    file://0009-Add-support-for-U9300C-TD-LTE-module.patch \
    file://0010-feat-Add-CP210x-driver-support-to-software-flow-cont.patch \
    file://0011-fix-disable-usb-lpm-to-fix-usb-device-reset.patch \
    file://0012-Fix-DP-maybe-not-display-problem.patch \
    file://0013-fix-fix-the-hardware-flow-function-of-cp2102n24.patch \
    file://0014-feat-add-io-expander-pcal9535-support.patch \
    file://0015-setting-the-RJ45-port-led-behavior.patch \
    file://0016-fix-clear-the-cycle-buffer-of-serial.patch \
    file://0017-feat-extend-led-panic-indicator-on-and-off.patch \
    file://0018-fix-can-not-auto-negotiate-to-100M-with-4-wire.patch \
    file://0019-feat-change-mmc-order-using-alias-in-dts.patch \
    file://0020-fix-PLL4_DCO-freq-over-range-cause-DP-not-display.patch \
    file://0021-serial-8250-8250_omap-Fix-possible-interrupt-storm-o.patch \
    file://0022-watchdog-add-support-for-adjusting-last-known-HW-kee.patch \
    file://0023-watchdog-use-__watchdog_ping-in-startup.patch \
    file://0024-watchdog-Respect-handle_boot_enabled-when-setting-la.patch \
    file://0025-watchdog-rti_wdt-Backport-mainline-driver.patch \
    file://0026-arm64-dts-ti-k3-am65-mcu-Switch-to-upstream-watchdog.patch \
    file://0027-scripts-dtc-Remove-redundant-YYLOC-global-declaratio.patch \
    "

KERNEL_BRANCH = "ti-sdk/processor-sdk-linux-4.19.y"
KERNEL_REV = "be5389fd85b69250aeb1ba477447879fb392152f"
SRC_URI[sha256sum] = "fb3ff6f856b9ae77f137a9a6f62c5dac05462fde40a12725351d49dec1dc811d"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"
KERNEL_DEFCONFIG_EXTRA = "iot2050_defconfig_extra.cfg"

S = "${WORKDIR}/processor-sdk-linux-${KERNEL_REV}"
