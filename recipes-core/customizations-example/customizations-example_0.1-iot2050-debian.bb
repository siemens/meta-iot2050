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
DEBIAN_DEPENDS = "openssh-server, bluez, pulseaudio-module-bluetooth, network-manager"

SRC_URI = " \
    file://status-led.service \
    file://postinst \
    file://10-globally-managed-devices.conf \
    file://cellular-4g \
    file://eno1-default \
    file://20-assign-ethernet-names.rules \
    file://20-create-symbolic-link-for-serial-port.rules \
    file://terminal_resize.sh"

do_install() {
    # add board status led service
    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/status-led.service ${D}/lib/systemd/system/

    # enable management via NetworkManager
    install -v -d ${D}/etc/NetworkManager/conf.d/
    install -v -m 600 ${WORKDIR}/10-globally-managed-devices.conf ${D}/etc/NetworkManager/conf.d/

    # add cellular support
    install -v -d ${D}/etc/NetworkManager/system-connections/
    install -v -m 600 ${WORKDIR}/cellular-4g ${D}/etc/NetworkManager/system-connections/

    # add eno1 default ip configuration
    install -v -m 600 ${WORKDIR}/eno1-default ${D}/etc/NetworkManager/system-connections/

    # swap ethernet port
    install -v -d  ${D}/etc/udev/rules.d/
    install -v -m 644 ${WORKDIR}/20-assign-ethernet-names.rules ${D}/etc/udev/rules.d/
    # create a symbolic link for serial port
    install -v -m 644 ${WORKDIR}/20-create-symbolic-link-for-serial-port.rules ${D}/etc/udev/rules.d/

    # resizing a terminal
    install -v -d ${D}/etc/profile.d/
    install -v -m 755 ${WORKDIR}/terminal_resize.sh ${D}/etc/profile.d
}
