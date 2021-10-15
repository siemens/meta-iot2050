#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT
inherit dpkg-raw

DEPENDS += "patch-u-boot-env"
DEBIAN_DEPENDS += "patch-u-boot-env"

SRC_URI += "file://99-watchdog.conf"

do_install[cleandirs] = "${D}/usr/lib/systemd/system.conf.d"
do_install() {
    install -m 0644 "${WORKDIR}/99-watchdog.conf" "${D}/usr/lib/systemd/system.conf.d"
}
