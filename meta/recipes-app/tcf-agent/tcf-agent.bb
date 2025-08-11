#
# Copyright (c) Siemens AG, 2019-2025
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

inherit dpkg

PV = "1.9.0-9076423f"
SRC_URI = " \
    git://gitlab.eclipse.org/eclipse/tcf/tcf.agent.git;protocol=https;branch=master \
    file://debian"
SRCREV = "9076423f959d53aafa4000d6bb8bf2a1485971b9"

S = "${WORKDIR}/git"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/
    deb_add_changelog
}
