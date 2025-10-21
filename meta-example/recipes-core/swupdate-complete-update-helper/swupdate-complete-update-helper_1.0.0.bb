#
# Copyright (c) Siemens AG, 2021-2023
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

PR = "1"

inherit dpkg-raw
DESCRIPTION = "Add script to confirm update"

SRC_URI = "file://complete_update.sh"

DEBIAN_DEPENDS = "efibootguard"

do_install() {
    install -v -d ${D}/usr/bin
    install -v -m 644 ${WORKDIR}/complete_update.sh ${D}/usr/bin/complete_update.sh
}
