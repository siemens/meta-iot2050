#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DESCRIPTION = "IOT2050 reference image customizations example"

# The bluez and pulseaudio-module-bluetooth must be install before this package,
# that's because the 'passwd --expire root' command in the 'postinst' file
DEBIAN_DEPENDS = "openssh-server, bluez, pulseaudio-module-bluetooth"

SRC_URI = " \
    file://status-led.service \
    file://postinst \
    file://board-configuration \
    file://board-configuration.service \
    file://board-configuration.json \
    file://10-globally-managed-devices.conf \
    file://cellular-4g \
    file://eth0-default \
    file://20-swap-ethernet-port.rules"

do_install() {
    # add board status led service
    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/status-led.service ${D}/lib/systemd/system/

    # add board configuration service
    install -v -d ${D}/usr/bin
    install -v -m 755 ${WORKDIR}/board-configuration ${D}/usr/bin
    install -v -m 644 ${WORKDIR}/board-configuration.service ${D}/lib/systemd/system/
    install -v -d ${D}/etc
    install -v -m 644 ${WORKDIR}/board-configuration.json ${D}/etc/

    # enable management via NetworkManager
    install -v -d ${D}/etc/NetworkManager/conf.d/
    install -v -m 600 ${WORKDIR}/10-globally-managed-devices.conf ${D}/etc/NetworkManager/conf.d/

    # add cellular support
    install -v -d ${D}/etc/NetworkManager/system-connections/
    install -v -m 600 ${WORKDIR}/cellular-4g ${D}/etc/NetworkManager/system-connections/

    # add eth0 default ip configuration
    install -v -m 600 ${WORKDIR}/eth0-default ${D}/etc/NetworkManager/system-connections/

    # swap ethernet port
    install -v -d  ${D}/etc/udev/rules.d/
    install -v -m 644 ${WORKDIR}/20-swap-ethernet-port.rules ${D}/etc/udev/rules.d/

}
