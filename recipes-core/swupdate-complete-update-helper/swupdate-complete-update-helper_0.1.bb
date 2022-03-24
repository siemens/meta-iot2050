#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg-raw
DESCRIPTION = "Add script to confirm update"

SRC_URI = "file://complete_update.sh"

do_install() {
    # add board status led service
    install -v -d ${D}/usr/bin
    install -v -m 644 ${WORKDIR}/complete_update.sh ${D}/usr/bin/complete_update.sh
}
