#
# Copyright (c) Siemens AG, 2021-2023
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DEBIAN_DEPENDS = "k3-rti-wdt, ti-pruss-firmware"
RDEPENDS = "k3-rti-wdt ti-pruss-firmware"

do_prepare_build:append() {
    echo "/lib/firmware/k3-rti-wdt.fw /lib/firmware/am65x-mcu-r5f0_0-fw" > ${S}/debian/links
}
