#
# Copyright (c) Siemens AG, 2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += " \
    https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/snapshot/ti-linux-kernel-${KERNEL_REV}.tar.xz;protocol=https; \
    file://0001-iot2050-add-iot2050-platform-support.patch \
    file://0002-feat-extend-led-panic-indicator-on-and-off.patch \
    file://0003-Workaround-to-correct-DP-clock-to-154MHZ.patch \
    file://0004-USB-serial-cp210x-return-early-on-unchanged-termios.patch \
    file://0005-USB-serial-cp210x-clean-up-line-control-handling.patch \
    file://0006-USB-serial-cp210x-set-terminal-settings-on-open.patch \
    file://0007-USB-serial-cp210x-drop-flow-control-debugging.patch \
    file://0008-USB-serial-cp210x-refactor-flow-control-handling.patch \
    file://0009-USB-serial-cp210x-clean-up-dtr_rts.patch \
    file://0010-USB-serial-cp210x-add-support-for-software-flow-cont.patch \
    file://0011-watchdog-Respect-handle_boot_enabled-when-setting-la.patch \
    file://0012-Bind-to-the-backported-rti_wdt-rather-than-the-legac.patch \
    file://0013-linux-dts-add-the-mboxes-properity-for-R5F-watchdog.patch \
    file://0014-dt-bindings-dp83867-Add-binding-for-the-status-led-c.patch \
    file://0015-net-phy-dp83867-implement-the-binding-for-status-led.patch \
    file://0016-iot2050-dts-add-the-phy-status-led-configuration.patch \
    file://0017-Pick-up-SDK-8.0-change-which-is-based-on-5.10-kernel.patch"

SRC_URI += " \
    file://${KERNEL_DEFCONFIG} \
    file://iot2050-upstream.cfg \
    file://iot2050_defconfig_extra.cfg"

KERNEL_REV = "4c2eade9f722838b0e457650368cba1c6c7483c2"
KERNEL_DEFCONFIG = "iot2050_defconfig_base"
SRC_URI[sha256sum] = "b085d9518ae5d57d211dc7c94f02c19a99d4e0397c191f20746bec8947583c04"

S = "${WORKDIR}/ti-linux-kernel-${KERNEL_REV}"
