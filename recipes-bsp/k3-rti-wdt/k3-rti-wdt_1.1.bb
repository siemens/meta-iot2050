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
SRCREV = "33a6680184996074ca9731710161520edf334725"

S = "${WORKDIR}/git"

DEBIAN_BUILD_DEPENDS += "gcc-arm-linux-gnueabihf"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize

    echo "k3-rti-wdt.fw /lib/firmware/" > ${S}/debian/install
}
