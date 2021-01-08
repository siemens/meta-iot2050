#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require u-boot-iot2050.inc

SRC_URI += " \
    https://gitlab.denx.de/u-boot/u-boot/-/archive/${U_BOOT_REV}/u-boot-${U_BOOT_REV}.tar.gz; \
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
    file://upstream/0012-arm-dts-k3-am65-main-Add-scm_conf-node.patch \
    file://upstream/0013-arm-dts-k3-am65-main-Add-pruss-nodes-for-ICSSG2.patch \
    file://upstream/0014-arm64-dts-ti-am654-base-board-add-ICSSG2-Ethernet-su.patch \
    file://upstream/0015-configs-am65x_evm_a53_defconfig-Enable-prueth-config.patch \
    file://upstream/0016-net-ti-icssg-prueth-Drop-unsupported-modes-from-the-.patch \
    file://upstream/0017-net-ti-icssg-prueth-use-constants-instead-of-hardcod.patch \
    file://upstream/0018-net-ti-icssg-prueth-use-a-single-chn_name-variable-i.patch \
    file://upstream/0019-net-ti-icssg-prueth-Add-port-speed-duplex-command.patch \
    file://upstream/0020-net-ti-icssg-prueth-Add-shutdown-command.patch \
    file://upstream/0021-net-ti-icssg-prueth-Auto-start-PRU-and-RTU-when-star.patch \
    file://upstream/0022-config_distro_bootcmd-Add-platform-start-script-hook.patch \
    file://upstream/0023-arm-dts-k3-am65-main-Add-ICSSG0-1-nodes.patch \
    file://upstream/0024-iot2050-Add-ICSSG0-Ethernet-support.patch \
    file://upstream/0025-iot2050-config-the-default-device-tree.patch \
    file://upstream/0026-mmc-Add-init-API.patch \
    file://upstream/0027-mmc-Add-a-saved_clock-member.patch \
    file://upstream/0028-spl-mmc-Fix-spl_mmc_get_uboot_raw_sector-implementat.patch \
    file://upstream/0029-mmc-sdhci-Add-helper-functions-for-UHS-modes.patch \
    file://upstream/0030-mmc-sdhci-Expose-sdhci_init-as-non-static.patch \
    file://upstream/0031-mmc-sdhci-Write-to-HOST_CONTROL2-register-for-HS400-.patch \
    file://upstream/0032-mmc-am654_sdhci-Get-Xin-clock-by-name.patch \
    file://upstream/0033-mmc-am654_sdhci-Create-driver_data-structure.patch \
    file://upstream/0034-mmc-am654_sdhci-Don-t-clear-iomux-for-j721e-8-bit-in.patch \
    file://upstream/0035-mmc-am654_sdhci-Add-Support-for-3-bit-frequency-sele.patch \
    file://upstream/0036-mmc-am654_sdhci-Add-set_ios_post-callback-for-j7-4-b.patch \
    file://upstream/0037-mmc-am654_sdhci-Add-Support-for-Strobe-Select.patch \
    file://upstream/0038-mmc-am654_sdhci-Add-Support-for-tuning.patch \
    file://upstream/0039-mmc-am654_sdhci-Update-output-tap-delay-writes.patch \
    file://upstream/0040-mmc-am654_sdhci-Use-the-generic-sdhci_set_control_re.patch \
    file://upstream/0041-mmc-am654_sdhci-Implement-workaround-for-card-detect.patch \
    file://upstream/0042-mmc-Move-the-ops-init-to-before-any-mmc_getcd-calls.patch \
    file://upstream/0043-mmc-am654_sdhci-Add-flag-for-PHY-calibration.patch \
    file://upstream/0044-mmc-am654_sdhci-Add-support-for-AM65x-SR2.0.patch \
    file://upstream/0045-mmc-am654_sdhci-Move-dll-related-configurations-to-i.patch \
    file://upstream/0046-mmc-am654_sdhci-Write-to-TXDLYCLK-when-not-enabling-.patch \
    file://upstream/0047-mmc-am654_sdhci-Add-support-for-writing-to-clkbuf_se.patch \
    file://upstream/0048-mmc-am654_sdhci-Use-MMC_MODES_END-value-instead-of-h.patch \
    file://upstream/0049-mmc-am654_sdhci-Unconditionally-switch-off-DLL-in-th.patch \
    file://upstream/0050-dm-soc-Introduce-UCLASS_SOC-for-SOC-ID-and-attribute.patch \
    file://upstream/0051-mmc-include-the-related-header.patch \
    "

U_BOOT_REV = "51f65b506f37252acb3cd4184ef5e1fc20da13a2"
U_BOOT_CONFIG = "iot2050_defconfig"
U_BOOT_BIN = "flash.bin"
SRC_URI[sha256sum] = "a92f0e88acaff78fa353f6e985165c72c2e6247bb2ca9c8e4356b5b3046d1857"
S = "${WORKDIR}/u-boot-${U_BOOT_REV}"

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
