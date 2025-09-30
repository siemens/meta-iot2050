#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "2"

inherit dpkg

DESCRIPTION = "Low Level Skeleton Library for Communication on GNU/Linux platforms"
MAINTAINER = "le.jin@siemens.com"
SRC_URI += "git://github.com/eclipse/mraa.git;protocol=https;branch=master \
            file://0001-gpio-Fix-JS-binding-regarding-interrupt-injections.patch \
            file://0002-common-increase-pin-name-size.patch \
            file://0003-iot2050-add-debugfs-pinmux-support.patch \
            file://0004-iot2050-Add-support-for-the-new-IOT2050-SM-variant.patch \
            file://0005-python-binding-Fix-Python-3.13-compatibility.patch \
            file://0006-javascript-update-C-standard-to-C-17-for-compatibili.patch \
            file://0007-fix-iot2050-Correct-parent-IDs-for-PWM-pins.patch \
            file://rules"

CHANGELOG_V = "${PV}-${PR}"
SRCREV = "8b1c54934e80edc2d36abac9d9c96fe1e01cb669"

S = "${WORKDIR}/git"

DEBIAN_BUILD_DEPENDS = " \
    cmake, \
    swig, \
    libpython3-dev, \
    nodejs, \
    libnode-dev, \
    libjson-c-dev, \
    default-jdk:native"

DEBIAN_DEPENDS = "python3, nodejs, \${shlibs:Depends}"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize

    echo "usr/share/java/mraa.jar usr/share/java/mraa-${PV}.jar" > ${S}/debian/mraa.links
}
