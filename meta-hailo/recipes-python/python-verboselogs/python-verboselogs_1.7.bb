# SPDX-FileCopyrightText: Copyright 2024 Siemens AG
# SPDX-License-Identifier: MIT

# Warning: This package seems abandoned. Latest commit is from 7 years ago

inherit dpkg

SRC_URI = "git://github.com/xolox/python-verboselogs.git;protocol=https;branch=master"
SRCREV ="3cebc69e03588bb6c3726c38c324b12732989292"

SRC_URI += " \
    file://debian/control \
    file://debian/rules \
"

S = "${WORKDIR}/git"

PROVIDES += "python3-verboselogs"

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
