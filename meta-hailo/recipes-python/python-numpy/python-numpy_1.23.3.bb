# SPDX-FileCopyrightText: Copyright 2024 Siemens AG
# SPDX-License-Identifier: MIT

inherit dpkg

SRC_URI = "https://github.com/numpy/numpy/archive/refs/tags/v1.23.3.tar.gz"
SRC_URI[sha256sum] = "d55da69341fd6e617ada55feec6798730457f26f08300956625c086499aced7e"

SRC_URI += " \
    file://debian/control \
    file://debian/rules \
"

S = "${WORKDIR}/numpy-1.23.3"

PROVIDES += "python3-numpy"

DEB_BUILD_PROFILES = "nocheck"
DEB_BUILD_OPTIONS = "nocheck"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize
    rm -f ${S}/debian/compat
    cp ${WORKDIR}/debian/control \
       ${WORKDIR}/debian/rules \
       ${S}/debian/
}