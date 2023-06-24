#
# CIP Core, generic profile
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg-raw

DEBIAN_DEPENDS = "initramfs-tools"

SRC_URI += "file://crash-demo.hook \
            file://crash-demo.script"

do_install[cleandirs] += " \
    ${D}/usr/share/initramfs-tools/hooks \
    ${D}/usr/share/initramfs-tools/scripts/local-top"

do_install() {
    install -m 0755 "${WORKDIR}/crash-demo.script" \
        "${D}/usr/share/initramfs-tools/scripts/local-top/crash-demo"
    install -m 0755 "${WORKDIR}/crash-demo.hook" \
        "${D}/usr/share/initramfs-tools/hooks/crash-demo"
}
