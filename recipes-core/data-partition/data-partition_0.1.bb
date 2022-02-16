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
           file://data.mount.tmpl"

FS_COMMIT_INTERVAL ?= "20"
TEMPLATE_VARS  += "FS_COMMIT_INTERVAL"
TEMPLATE_FILES += "data.mount.tmpl"

inherit dpkg-raw

do_install() {
    install -m 0755 -d ${D}/data
    touch ${D}/data/.keep

    TARGET=${D}/lib/systemd/system
    install -m 0755 -d ${TARGET}
    install -m 0644 ${WORKDIR}/data.mount ${TARGET}/data.mount
}

addtask do_install after do_transform_template
