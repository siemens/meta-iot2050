#
# Copyright (c) Siemens AG, 2018-2022
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

SRC_URI[sha256sum] = "e642fc604b611dc6f3e8382447fb2bc4047d129a14cba3996d34b85e07ae9d3a"

SRC_URI += "file://iot2050-rt.cfg"
