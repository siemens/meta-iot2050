#
# Copyright (c) Siemens AG, 2023
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DESCRIPTION = "Add hotplug Display Port support for Light Desktop Manager"

DEBIAN_DEPENDS = "lightdm,systemd"

SRC_URI = "file://postinst"
