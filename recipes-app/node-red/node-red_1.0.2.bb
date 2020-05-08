#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Nian Gao <nian.gao@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit npm

DESCRIPTION = "A visual tool for wiring the Internet of Things"

PRESERVE_PERMS = "usr/lib/node_modules/node-red/red.js"

SRC_URI += "file://node-red.service"

do_install_append() {
    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/node-red.service ${D}/lib/systemd/system/
}
