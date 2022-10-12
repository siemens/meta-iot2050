#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
inherit dpkg

DESCRIPTION = "A Powerful Diagnostic Tool for Texas Instruments K3 based Processors"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI += "https://git.ti.com/cgit/k3conf/k3conf/snapshot/k3conf-0.2.tar.gz;protocol=https \
            file://debian"
SRC_URI[sha256sum] = "4e19f6fdee6d40216d786c7d9000191771fe3ff467e5b5efe659ad5acb6f610f"

S = "${WORKDIR}/k3conf-${PV}"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/
    deb_debianize
}

