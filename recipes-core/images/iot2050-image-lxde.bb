#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-core/images/iot2050-image-example.bb

DESCRIPTION = "IOT2050 LXDE Image"

IMAGE_INSTALL += "lxde-touch"
