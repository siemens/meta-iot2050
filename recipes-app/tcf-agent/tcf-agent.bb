#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

PV = "1.8.0-1f11747e"
SRC_URI = " \
    git://gitlab.eclipse.org/eclipse/tcf/tcf.agent.git;protocol=https;branch=master \
    file://debian"
SRCREV = "1f11747e83ebf4f53e8d17f430136f92ec378709"

S = "${WORKDIR}/git"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/
    deb_add_changelog
}
