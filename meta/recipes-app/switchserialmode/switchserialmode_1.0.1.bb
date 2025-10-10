#
# Copyright (c) Siemens AG, 2019-2025
#
# Authors:
#  Gao Nian <nian.gao@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "2"

inherit dpkg

DESCRIPTION = "Tool to switch between the uart0 modes"
MAINTAINER = "nian.gao@siemens.com"

SRC_URI = "file://src"

S = "${WORKDIR}/src"

PROVIDES := "${BPN}"
DEBIAN_CONFLICTS := "${BPN}"
DEBIAN_PROVIDES := "${BPN}"
DEBIAN_REPLACES := "${BPN}"
DEBIAN_BUILD_DEPENDS = "cmake, libusb-1.0-0-dev, libgpiod-dev, pkg-config"
DEBIAN_DEPENDS = "\${shlibs:Depends}"
PN := "iot2050-${BPN}"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize
}
