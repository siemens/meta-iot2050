#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

SRC_URI += " \
    https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/snapshot/ti-linux-kernel-${KERNEL_REV}.tar.xz;protocol=https; \
    file://0001-iot2050-add-iot2050-platform-support.patch \
    file://0002-feat-extend-led-panic-indicator-on-and-off.patch \
    file://0003-feat-change-mmc-order-using-alias-in-dts.patch \
    file://0004-Workaround-to-correct-DP-clock-to-154MHZ.patch \
    file://0005-gpio-pca953x-Add-support-for-the-PCAL9535.patch \
    file://0006-USB-serial-cp210x-disable-interface-on-errors-in-ope.patch \
    file://0007-USB-serial-cp210x-add-support-for-line-status-events.patch \
    file://0008-USB-serial-cp210x-add-support-for-TIOCGICOUNT.patch \
    file://0009-USB-serial-cp210x-drop-unnecessary-packed-attributes.patch \
    file://0010-USB-serial-cp210x-use-in-kernel-types-in-port-data.patch \
    file://0011-USB-serial-cp210x-return-early-on-unchanged-termios.patch \
    file://0012-USB-serial-cp210x-clean-up-line-control-handling.patch \
    file://0013-USB-serial-cp210x-set-terminal-settings-on-open.patch \
    file://0014-USB-serial-cp210x-drop-flow-control-debugging.patch \
    file://0015-USB-serial-cp210x-refactor-flow-control-handling.patch \
    file://0016-USB-serial-cp210x-clean-up-dtr_rts.patch \
    file://0017-USB-serial-cp210x-add-support-for-software-flow-cont.patch \
    file://0018-watchdog-rti-wdt-attach-to-running-watchdog-during-p.patch \
    file://0019-watchdog-use-__watchdog_ping-in-startup.patch \
    file://0020-watchdog-add-support-for-adjusting-last-known-HW-kee.patch \
    file://0021-watchdog-Respect-handle_boot_enabled-when-setting-la.patch \
    file://0022-Bind-to-the-backported-rti_wdt-rather-than-the-legac.patch \
    file://0023-linux-dts-add-the-mboxes-properity-for-R5F-watchdog.patch \
    file://0024-dt-bindings-dp83867-Add-binding-for-the-status-led-c.patch \
    file://0025-net-phy-dp83867-implement-the-binding-for-status-led.patch \
    file://0026-iot2050-dts-add-the-phy-status-led-configuration.patch"

SRC_URI += " \
    file://${KERNEL_DEFCONFIG} \
    file://iot2050-upstream.cfg \
    file://iot2050_defconfig_extra.cfg"

KERNEL_REV = "9574bba32a1898794895ca3816e815154c80226d"
KERNEL_DEFCONFIG = "iot2050_defconfig_base"
SRC_URI[sha256sum] = "59fc1e9ec4af575837a3afe30e031b9f689b759b87c8414099dd05579a9e7b3d"

S = "${WORKDIR}/ti-linux-kernel-${KERNEL_REV}"
