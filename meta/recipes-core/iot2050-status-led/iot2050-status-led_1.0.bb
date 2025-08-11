#
# Copyright (c) Siemens AG, 2019-2025
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 led status service"

SRC_URI = " \
    file://postinst \
    file://status-led.service \
"

do_install() {
    # add board status led service
    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/status-led.service ${D}/lib/systemd/system/
}
