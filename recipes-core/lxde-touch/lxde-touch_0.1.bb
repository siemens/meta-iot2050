#
# Copyright (c) Siemens AG, 2018
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DESCRIPTION = "LXDE desktop with touch display support"

DEBIAN_DEPENDS = "task-desktop, xdg-utils, task-lxde-desktop, lxtask, onboard"

SRC_URI = "file://postinst"
