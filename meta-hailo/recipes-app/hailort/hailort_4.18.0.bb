# SPDX-FileCopyrightText: Copyright 2023-2024 Siemens AG
# SPDX-License-Identifier: MIT
DESCRIPTION = "userspace API for running inference on the hailo8 chip"

LICENSE = "MIT"

inherit dpkg

HAILO_EXTERNAL_DIR = "${P}/hailort/external"

SRC_URI = " \
    git://git@github.com/hailo-ai/hailort.git;protocol=https;branch=master;name=hailort;destsuffix=${P} \
    git://github.com/hailo-ai/CLI11.git;protocol=https;nobranch=1;name=cli11;destsuffix=${HAILO_EXTERNAL_DIR}/cli11-src \
    git://github.com/hailo-ai/DotWriter.git;protocol=https;nobranch=1;name=dotwriter;destsuffix=${HAILO_EXTERNAL_DIR}/dotwriter-src"
SRC_URI += " \
    file://patches/0001-do-not-use-spdlog-formatting-internals.patch \
    file://patches/0002-use-distro-version-of-packages-if-possible.patch \
    file://patches/0003-install-independent-of-build-target.patch \
    file://patches/0004-install-python-bindings-into-dist-packages.patch \
    file://patches/0005-Fix-cross-compilation-issue-for-pybuild.patch \
"

SRC_URI += " \
    file://debian/control \
    file://debian/hailort.install \
    file://debian/hailort.service \
    file://debian/hailortcli.install \
    file://debian/libhailort-dev.install \
    file://debian/libhailort.install \
    file://debian/python3-hailort.install \
    file://debian/libgsthailo.install \
    file://debian/libgsthailo-dev.install \
    file://debian/not-installed \
    file://debian/rules \
    file://debian/python-numpy.pref \
"

DEPENDS += "python3-verboselogs python3-numpy"
PROVIDES += "hailortcli libhailort libhailort-dev python3-hailort libgsthailo libgsthailo-dev"

SRCREV_hailort = "01e4c7f5a7463cc61ef1b2d22c31dd80a3a07d95"
SRCREV_cli11 = "ae78ac41cf225706e83f57da45117e3e90d4a5b4"
SRCREV_dotwriter = "e5fa8f281adca10dd342b1d32e981499b8681daf"

S = "${WORKDIR}/${P}"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize
    rm -f ${S}/debian/compat
    cp -r ${WORKDIR}/debian/* ${S}/debian/
}
