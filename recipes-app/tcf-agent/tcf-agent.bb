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

PV = "1.7.0-86584ece"
SRC_URI = " \
    git://git.eclipse.org/r/tcf/org.eclipse.tcf.agent.git;protocol=https;branch=master \
    file://debian"
SRCREV = "86584ece496308711bbd5733f097aa4d4d84aec3"

S = "${WORKDIR}/git"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/
    deb_add_changelog
}
