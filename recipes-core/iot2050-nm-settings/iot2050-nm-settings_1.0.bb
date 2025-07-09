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

DESCRIPTION = "IOT2050 reference image customizations network"

DEBIAN_DEPENDS = "network-manager"

SRC_URI = " \
    file://postinst \
    file://10-globally-managed-devices.conf \
    file://cellular-4g \
    file://eno1-default"

do_install() {
    # enable management via NetworkManager
    install -v -d ${D}/etc/NetworkManager/conf.d/
    install -v -m 600 ${WORKDIR}/10-globally-managed-devices.conf ${D}/etc/NetworkManager/conf.d/

    # add cellular support
    install -v -d ${D}/etc/NetworkManager/system-connections/
    install -v -m 600 ${WORKDIR}/cellular-4g ${D}/etc/NetworkManager/system-connections/

    # add eno1 default ip configuration
    install -v -m 600 ${WORKDIR}/eno1-default ${D}/etc/NetworkManager/system-connections/
}
