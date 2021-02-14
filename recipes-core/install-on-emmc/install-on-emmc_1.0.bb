#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg-raw

DESCRIPTION = "This service provides the option to install on eMMC during first boot"

DEPENDS = "regen-rootfs-uuid"
DEBIAN_DEPENDS = "systemd, fdisk, util-linux, regen-rootfs-uuid"

SRC_URI = " \
    file://install-on-emmc-on-first-boot.service \
    file://install-on-emmc.sh \
    file://postinst"

do_install() {
    install -d -m 755 ${D}/lib/systemd/system
    install -m 644 ${WORKDIR}/install-on-emmc-on-first-boot.service ${D}/lib/systemd/system/

    install -d -m 755 ${D}/usr/share/install-on-emmc
    install -m 755 ${WORKDIR}/install-on-emmc.sh ${D}/usr/share/install-on-emmc/
}
