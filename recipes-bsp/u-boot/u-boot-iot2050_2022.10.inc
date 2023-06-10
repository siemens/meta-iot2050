#
# Copyright (c) Siemens AG, 2020-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Su Baocheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2 \
    file://0001-efi_loader-Improve-console-screen-clearing-and-reset.patch \
    file://0002-env-Complete-generic-support-for-writable-list.patch \
    file://0003-env-Couple-networking-related-variable-flags-to-CONF.patch \
    file://0004-tools-Add-script-for-converting-public-key-into-devi.patch \
    file://0005-board-siemens-iot2050-Split-the-build-for-PG1-and-PG.patch \
    file://0006-arm-dts-iot2050-Use-the-auto-generator-nodes-for-fdt.patch \
    file://0007-iot2050-Update-firmware-layout.patch \
    file://0008-iot2050-Add-watchdog-start-to-bootcmd.patch \
    file://0009-iot2050-Add-CONFIG_ENV_FLAGS_LIST_STATIC.patch \
    file://0010-arm-dts-iot2050-Allow-verifying-U-Boot-proper-by-SPL.patch \
    file://0011-iot2050-Add-script-for-signing-artifacts.patch \
    file://0012-arm-dts-iot2050-Optionally-embed-OTP-programming-dat.patch \
    file://0013-doc-iot2050-Add-a-note-about-the-watchdog-firmware.patch \
    file://0014-board-siemens-iot2050-use-the-named-gpio-to-control-.patch \
    file://0015-arm-dts-iot2050-Add-support-for-M.2-variant.patch \
    file://0016-iot2050-Add-support-for-configuring-M.2-connector.patch \
    file://0017-spl-fit-Report-fdt-error-for-loading-u-boot.patch \
    file://0018-efi_loader-Let-networking-support-depend-on-NETDEVIC.patch \
    file://0019-iot2050-Refactor-the-m.2-and-minipcie-power-pin.patch \
    "

SRC_URI[sha256sum] = "50b4482a505bc281ba8470c399a3c26e145e29b23500bc35c50debd7fa46bdf8"

S = "${WORKDIR}/u-boot-${PV}"
