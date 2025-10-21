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

DESCRIPTION = "Set NODE_PATH for nodejs"

SRC_URI = " \
    file://postinst \
"
