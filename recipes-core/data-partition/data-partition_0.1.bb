#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

DESCRIPTION = "data systemd-mount"

DEBIAN_DEPENDS = "systemd"

SRC_URI = "file://postinst \
           file://initramfs.fsck.hook \
           file://data.mount"


inherit dpkg-raw

do_install() {
    install -m 0755 -d ${D}/data
    touch ${D}/data/.keep

    TARGET=${D}/lib/systemd/system
    install -m 0755 -d ${TARGET}
    install -m 0644 ${WORKDIR}/data.mount ${TARGET}/data.mount

    TARGET=${D}/etc/initramfs-tools/hooks
    install -m 0755 -d ${TARGET}
    install -m 0740 ${WORKDIR}/initramfs.fsck.hook ${TARGET}/fsck.ext4.hook
}

addtask do_install after do_transform_template
