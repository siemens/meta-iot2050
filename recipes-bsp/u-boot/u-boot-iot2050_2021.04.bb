#
# Copyright (c) Siemens AG, 2020-2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2 \
    file://upstream/0001-arm-dts-Add-IOT2050-device-tree-files.patch \
    file://upstream/0002-board-siemens-Add-support-for-SIMATIC-IOT2050-device.patch \
    file://upstream/0003-watchdog-rti_wdt-Add-support-for-loading-firmware.patch \
    file://upstream/0004-net-eth-uclass-eth_get_dev-based-on-SEQ_ALIAS-instea.patch \
    file://upstream/0005-net-eth-uclass-call-stop-only-for-active-devices.patch \
    file://upstream/0006-misc-uclass-Introduce-misc_init_by_ofnode.patch \
    file://upstream/0007-soc-ti-pruss-add-a-misc-driver-for-PRUSS-in-TI-SoCs.patch \
    file://upstream/0008-remoteproc-pruss-add-PRU-remoteproc-driver.patch \
    file://upstream/0009-net-ti-icssg-prueth-Add-ICSSG-ethernet-driver.patch \
    file://upstream/0010-arm-dts-k3-am65-main-Add-msmc_ram-node.patch \
    file://upstream/0011-arm-dts-k3-am654-base-board-u-boot-Add-icssg-specifi.patch \
    file://upstream/0012-arm-dts-k3-am65-main-Add-pruss-nodes-for-ICSSG2.patch \
    file://upstream/0013-arm64-dts-ti-am654-base-board-add-ICSSG2-Ethernet-su.patch \
    file://upstream/0014-configs-am65x_evm_a53_defconfig-Enable-prueth-config.patch \
    file://upstream/0015-net-ti-icssg-prueth-Drop-unsupported-modes-from-the-.patch \
    file://upstream/0016-net-ti-icssg-prueth-use-constants-instead-of-hardcod.patch \
    file://upstream/0017-net-ti-icssg-prueth-use-a-single-chn_name-variable-i.patch \
    file://upstream/0018-net-ti-icssg-prueth-Add-port-speed-duplex-command.patch \
    file://upstream/0019-net-ti-icssg-prueth-Add-shutdown-command.patch \
    file://upstream/0020-net-ti-icssg-prueth-Auto-start-PRU-and-RTU-when-star.patch \
    file://upstream/0021-config_distro_bootcmd-Add-platform-start-script-hook.patch \
    file://upstream/0022-arm-dts-k3-am65-main-Add-ICSSG0-1-nodes.patch \
    file://upstream/0023-iot2050-Add-ICSSG0-Ethernet-support.patch \
    file://upstream/0024-arm64-dts-ti-k3-am65-mcu-Add-RTI-watchdog-entry.patch \
    "

U_BOOT_CONFIG = "iot2050_defconfig"
U_BOOT_BIN = "flash.bin"
SRC_URI[sha256sum] = "0d438b1bb5cceb57a18ea2de4a0d51f7be5b05b98717df05938636e0aadfe11a"

S = "${WORKDIR}/u-boot-${PV}"

SPI_FLASH_IMG = "${U_BOOT_BIN}"
SPI_FLASH_DEPLOY_IMG = "iot2050-image-boot.bin"

DEPENDS += "trusted-firmware-a-iot2050 optee-os-iot2050"
DEBIAN_BUILD_DEPENDS =. "trusted-firmware-a-iot2050, optee-os-iot2050, \
    swig:native, python3-dev:native, python3-pkg-resources,"

do_prepare_build_append() {
    cd ${S}
    ln -sf ../prebuild/* ${S}
}

dpkg_runbuild_prepend() {
    export ATF=/usr/lib/trusted-firmware-a/iot2050/bl31.bin
    export TEE=/usr/lib/optee-os/iot2050/tee-pager_v2.bin
}
