#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
inherit dpkg

DESCRIPTION = "Low Level Skeleton Library for Communication on GNU/Linux platforms"
MAINTAINER = "le.jin@siemens.com"
SRC_URI += "git://github.com/eclipse/mraa.git;protocol=https \
            file://rules"
SRCREV = "8b1c54934e80edc2d36abac9d9c96fe1e01cb669"

S = "${WORKDIR}/git"

DEPENDS = "swig"

DEBIAN_BUILD_DEPENDS = " \
    cmake, \
    swig4.0, \
    libpython3-dev, \
    nodejs, \
    libnode-dev, \
    libjson-c-dev, \
    default-jdk:native"

DEBIAN_DEPENDS = "python3, nodejs"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize

    echo "usr/share/java/mraa.jar usr/share/java/mraa-${PV}.jar" > ${S}/debian/mraa.links
}
