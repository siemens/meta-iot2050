#
# Copyright (c) Siemens AG, 2020-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Baocheng Su <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT

PR = "1"

inherit dpkg-raw

DESCRIPTION = "This service generates individual PARTUUIDs for the boot device during first boot"

DEBIAN_DEPENDS = "systemd, gdisk, util-linux"

SRC_URI = " \
    file://regen-bootdev-partuuid-on-first-boot.service \
    file://regen-bootdev-partuuid.sh \
    file://postinst"

do_install() {
    install -d -m 755 ${D}/usr/lib/systemd/system
    install -m 644 ${WORKDIR}/regen-bootdev-partuuid-on-first-boot.service ${D}/usr/lib/systemd/system/

    install -d -m 755 ${D}/usr/share/regen-bootdev-partuuid
    install -m 755 ${WORKDIR}/regen-bootdev-partuuid.sh ${D}/usr/share/regen-bootdev-partuuid/
}
