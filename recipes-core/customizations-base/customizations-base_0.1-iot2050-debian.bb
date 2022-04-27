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

# optional local customizations, not part of the repository
include local.inc

DESCRIPTION = "IOT2050 reference image customizations"

SRC_URI = "file://postinst.tmpl"

TEMPLATE_FILES = "postinst.tmpl"
TEMPLATE_VARS = "HOSTNAME"

DEBIAN_DEPENDS = "netbase"
