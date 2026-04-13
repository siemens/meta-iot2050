#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "4"

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
            file://0008-fix-GPIOs-that-number-is-larger-than-512-cannot-trig.patch \
            file://0009-gpio-chardev-init-compatibility.patch \
            file://0010-gpio-chardev-add-support-for-more-direction-flags.patch \
            file://0011-gpio-chardev-fix-ressource-handling.patch \
            file://0012-iot2050-add-helper-function-to-convert-gpio-number-t.patch \
            file://0013-iot2050-add-support-for-gpio-chardev-interface.patch \
            file://0014-iot2050-fix-pinmux-handling-of-user-pin.patch \
            file://0015-gpio-fix-fd-and-memory-leaks-in-gpiod-chardev-init-p.patch \
            file://20-mraa-permissions.rules \
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
    
    cp ${WORKDIR}/20-mraa-permissions.rules ${S}/debian/20-mraa-permissions.rules
    echo "debian/20-mraa-permissions.rules etc/udev/rules.d" > ${S}/debian/install
    echo "usr/share/java/mraa.jar usr/share/java/mraa-${PV}.jar" > ${S}/debian/mraa.links
}
