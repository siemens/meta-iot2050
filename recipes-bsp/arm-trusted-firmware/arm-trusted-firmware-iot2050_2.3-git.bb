#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

SRC_URI = " \
    git://github.com/ARM-software/arm-trusted-firmware.git;protocol=https \
    file://rules"
SRCREV = "568a8817281d6acb80580226dfcb4e39edcb74c1"

DEBIAN_BUILD_DEPENDS = "git"

S = "${WORKDIR}/git"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize

    echo "build/k3/generic/release/bl31.bin /usr/lib/arm-trusted-firmware/iot2050/" > ${S}/debian/install
}
