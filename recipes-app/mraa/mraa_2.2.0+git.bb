#
# Copyright (c) Siemens AG, 2019-2023
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
SRC_URI += "git://github.com/eclipse/mraa.git;protocol=https;branch=master \
            file://0001-gpio-Fix-JS-binding-regarding-interrupt-injections.patch \
            file://0002-common-increase-pin-name-size.patch \
            file://0003-iot2050-add-debugfs-pinmux-support.patch \
            file://0004-iot2050-Add-support-for-the-new-IOT2050-SM-variant.patch \
            file://0005-gpio-chardev-init-compatibility.patch \
            file://0006-gpio-chardev-add-support-for-more-direction-flags.patch \
            file://0007-gpio-chardev-fix-ressource-handling.patch \
            file://0008-iot2050-add-helper-function-to-convert-gpio-number-t.patch \
            file://0009-iot2050-add-support-for-gpio-chardev-interface.patch \
            file://20-mraa-permissions.rules \
            file://rules"
SRCREV = "8b1c54934e80edc2d36abac9d9c96fe1e01cb669"

S = "${WORKDIR}/git"

DEBIAN_BUILD_DEPENDS = " \
    cmake, \
    swig4.0, \
    libpython3-dev, \
    nodejs, \
    libnode-dev, \
    libjson-c-dev, \
    default-jdk:native"

DEBIAN_DEPENDS = "python3, nodejs, \${shlibs:Depends}"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize

    cp ${WORKDIR}/20-mraa-permissions.rules ${S}/debian/20-mraa-permissions.rules
    echo "debian/20-mraa-permissions.rules etc/udev/rules.d" > ${S}/debian/install
    echo "usr/share/java/mraa.jar usr/share/java/mraa-${PV}.jar" > ${S}/debian/mraa.links
}
