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

DESCRIPTION = "IOT2050 base packages"

SRC_URI = "file://postinst.tmpl \
           file://20-assign-ethernet-names.rules \
           file://20-create-symbolic-link-for-serial-port.rules \
           file://terminal_resize.sh"

TEMPLATE_FILES = "postinst.tmpl"
TEMPLATE_VARS = "HOSTNAME"

DEBIAN_DEPENDS = "netbase"

do_install() {
    # swap ethernet port
    install -v -d  ${D}/etc/udev/rules.d/
    install -v -m 644 ${WORKDIR}/20-assign-ethernet-names.rules ${D}/etc/udev/rules.d/

    # resizing a terminal
    install -v -d ${D}/etc/profile.d/
    install -v -m 755 ${WORKDIR}/terminal_resize.sh ${D}/etc/profile.d
}
