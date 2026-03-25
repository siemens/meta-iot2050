#
# Copyright (c) Siemens AG, 2019-2025
#
# Authors:
#  Nian Gao <nian.gao@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
# To update the npm-shrinkwrap.json file, ensure you follow the guidelines
# provided in meta-node-red/classes/npm.bbclass.
#

PR = "2"

inherit npm
require recipes-app/node-red/node-red-home.inc

DESCRIPTION = "A visual tool for wiring the Internet of Things"

PRESERVE_PERMS = "usr/lib/node_modules/node-red/red.js"
DEBIAN_DEPENDS = "nodejs"

SRC_URI += "file://node-red.service.tmpl \
            file://99-node-red.preset"

TEMPLATE_FILES = "node-red.service.tmpl"
TEMPLATE_VARS  = "NODE_RED_HOME_DIR"

do_prepare_build:append() {
    cat <<EOF >> ${S}/debian/rules

override_dh_installsystemd:
	dh_installsystemd --no-start
EOF
}

do_install:append() {
    install -v -d ${D}/usr/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/node-red.service ${D}/usr/lib/systemd/system/

    install -v -d ${D}/usr/lib/systemd/system-preset/
    install -v -m 644 ${WORKDIR}/99-node-red.preset ${D}/usr/lib/systemd/system-preset/
}
