#
# Copyright (c) Siemens AG, 2021-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

SRC_URI = " \
    git://github.com/siemens/k3-rti-wdt.git;protocol=https;branch=master \
    file://rules"
SRCREV = "806a7597d7853962d3eaac6340067829af0306c0"

S = "${WORKDIR}/git"

DEBIAN_BUILD_DEPENDS += "gcc-arm-linux-gnueabihf"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize

    echo "k3-rti-wdt.fw /lib/firmware/" > ${S}/debian/install
}
