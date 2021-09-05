#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

PV = "1.7.0-f577ec33"
SRC_URI = " \
    git://git.eclipse.org/r/tcf/org.eclipse.tcf.agent.git;protocol=https \
    file://debian"
SRCREV = "f577ec3314aebdce3c9c61d982049129ab8eee94"

S = "${WORKDIR}/git"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/
    deb_add_changelog
}
