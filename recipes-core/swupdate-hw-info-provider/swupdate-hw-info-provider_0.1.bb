#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Felix Moessbauer <felix.moessbauer@siemens.com>
#
# SPDX-License-Identifier: MIT
#
# Note: This service writes the second element from /proc/device-tree/compatible
#       into /etc/hwrevision. For an IOT2050 Advanced PG2, this mapps to:
#       "iot2050-advanced-pg2ti"

inherit dpkg
DESCRIPTION = "one-shot service to initialize hardware info for swupdate"

SRC_URI = "file://swupdate-hw-info-provider.service"
DPKG_ARCH = "all"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize
    cp ${WORKDIR}/swupdate-hw-info-provider.service ${S}/debian
}
