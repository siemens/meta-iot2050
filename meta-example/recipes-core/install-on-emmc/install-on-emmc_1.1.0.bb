#
# Copyright (c) Siemens AG, 2021-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg-raw

PR="1"

DESCRIPTION = "This service provides the option to install on eMMC during first boot"

DEBIAN_DEPENDS = "systemd, init-system-helpers, fdisk, util-linux, parted"

SRC_URI = " \
    file://install-on-emmc-on-first-boot.service \
    file://install-on-emmc.sh \
    file://postinst"

do_install() {
    install -d -m 755 ${D}/usr/lib/systemd/system
    install -m 644 ${WORKDIR}/install-on-emmc-on-first-boot.service ${D}/usr/lib/systemd/system/

    install -d -m 755 ${D}/usr/share/install-on-emmc
    install -m 755 ${WORKDIR}/install-on-emmc.sh ${D}/usr/share/install-on-emmc/
}
