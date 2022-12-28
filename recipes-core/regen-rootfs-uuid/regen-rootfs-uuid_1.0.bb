#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg-raw

DESCRIPTION = "This service generates an individual UUID for the rootfs during first boot"

RDEPENDS = "u-boot-script"
DEBIAN_DEPENDS = "systemd, u-boot-script, fdisk, util-linux, uuid-runtime"

SRC_URI = " \
    file://regen-rootfs-uuid-on-first-boot.service \
    file://regen-rootfs-uuid.sh \
    file://postinst"

do_install() {
    install -d -m 755 ${D}/lib/systemd/system
    install -m 644 ${WORKDIR}/regen-rootfs-uuid-on-first-boot.service ${D}/lib/systemd/system/

    install -d -m 755 ${D}/usr/share/regen-rootfs-uuid
    install -m 755 ${WORKDIR}/regen-rootfs-uuid.sh ${D}/usr/share/regen-rootfs-uuid/
}
