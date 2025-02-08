# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: MIT
DESCRIPTION = "application examples, pipeline elements and pre-trained AI for Hailo8"
LICENSE = "MIT"

inherit dpkg

SRC_URI = "git://git@github.com/hailo-ai/tappas.git;protocol=https;name=tappas;branch=master;destsuffix=${P}"
SRCREV_tappas = "4327923422ababaf3a9395f86bf39f5b34dcfd83"

SRC_URI += " \
    file://debian/control \
    file://debian/rules \
"

DEPENDS += " hailort "
PROVIDES += " tappas-apps"
# PROVIDES += " libgsthailotools tappas-apps hailo-post-processes tappas-tracers"

S = "${WORKDIR}/${P}"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_add_changelog
    cp -r ${WORKDIR}/debian/* ${S}/debian/
}
