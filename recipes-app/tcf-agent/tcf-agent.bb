#
# Copyright (c) Siemens AG, 2019-2022
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

PV = "1.7.0-a199cc0e"
SRC_URI = " \
    git://git.eclipse.org/r/tcf/org.eclipse.tcf.agent.git;protocol=https \
    file://debian"
SRCREV = "a199cc0e59f7edb5f2f38eceb2c7feb1073cce3b"

S = "${WORKDIR}/git"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/
    deb_add_changelog
}
