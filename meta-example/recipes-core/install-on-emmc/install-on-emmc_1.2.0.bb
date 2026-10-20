#
# Copyright (c) Siemens AG, 2021-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#  Baocheng Su <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg-raw

PR="1"

DESCRIPTION = "This service provides the option to install on eMMC during first boot"

DEBIAN_DEPENDS = "systemd, jq, fdisk, gdisk, util-linux"

IOT2050_INSTALL_ON_EMMC_AUTO ?= "0"

SRC_URI = " \
    file://install-on-emmc-on-first-boot.service \
    file://install-on-emmc.sh \
    file://postinst"

do_install() {
    install -d -m 755 ${D}/usr/lib/systemd/system
    install -m 644 ${WORKDIR}/install-on-emmc-on-first-boot.service ${D}/usr/lib/systemd/system/

    install -d -m 755 ${D}/usr/share/install-on-emmc
    install -m 755 ${WORKDIR}/install-on-emmc.sh ${D}/usr/share/install-on-emmc/

    if [ "${IOT2050_INSTALL_ON_EMMC_AUTO}" = "1" ]; then
        install -d -m 755 ${D}/etc
        touch ${D}/etc/install-on-emmc
    fi
}
