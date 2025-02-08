# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
# SPDX-FileContributor: Authored by Li Hua Qian <huaqian.li@siemens.com>

DESCRIPTION = "application examples, pipeline elements and pre-trained AI for Hailo8"
LICENSE = "MIT"

inherit dpkg

SRC_URI = "git://git@github.com/hailo-ai/tappas.git;protocol=https;name=tappas;branch=master;destsuffix=${P}"
# Tappas v3.29.1-vpu-v1.4.1
SRCREV_tappas = "4327923422ababaf3a9395f86bf39f5b34dcfd83"

SRC_URI += " \
    file://debian/control \
    file://debian/rules \
    file://debian/libgsthailotools.install \
    file://debian/tappas-apps.install \
    file://debian/hailo-post-processes.install \
    file://debian/tappas-tracers.install \
    file://debian/not-installed \
    file://files/patches/0001-tappas-Adapt-tappas-apps-for-compatibility-with-meta.patch \
"

DEPENDS += " hailort "
PROVIDES += " libgsthailotools tappas-apps hailo-post-processes tappas-tracers"

S = "${WORKDIR}/${P}"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_add_changelog
    cp -r ${WORKDIR}/debian/* ${S}/debian/
}
