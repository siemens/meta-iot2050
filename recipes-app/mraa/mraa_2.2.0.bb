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
            file://0001-aio.c-fix-mraa_aio_set_bit-for-result-scaling.patch \
            file://0002-feat-iot2050-add-iot2050-platform-support.patch \
            file://0003-feat-iot2050-add-some-example-code-for-testing.patch \
            file://0004-api-Add-explicit-close-methods-to-classes.patch \
            file://0005-gpio-chardev-Add-helper-to-retrieve-gpiochip-and-lin.patch \
            file://0006-gpio-chardev-Add-function-to-retrieve-sysfs-base-for.patch \
            file://0007-iot2050-Switch-to-runtime-detection-of-gpiochip-numb.patch \
            file://0008-iot2050-Add-USER-button.patch \
            file://0009-led-Fix-and-cleanup-initialization.patch \
            file://0010-uart-Fix-software-flow-control-management.patch \
            file://0011-gpio-Avoid-spurious-value-reset-without-output-mode-.patch \
            file://0012-version.h-Fix-multiple-definitions-of-gVERSION-_SHOR.patch \
            file://0013-Support-for-swig-4.1.0.patch \
            file://rules"
SRCREV = "7786c7ded5c9ce7773890d0e3dc27632898fc6b1"

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
