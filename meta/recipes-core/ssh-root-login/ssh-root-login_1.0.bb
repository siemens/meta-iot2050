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

DESCRIPTION = "Permit root login for ssh"

DEBIAN_DEPENDS = "openssh-server"

SRC_URI = " \
    file://postinst \
"
