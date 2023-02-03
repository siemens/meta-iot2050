#
# Copyright (c) Siemens AG, 2018-2023
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

SRC_URI[sha256sum] = "b5539243f187e3d478d76d44ae13aab83952c94b885ad889df6fa9997e16a441"

SRC_URI += "file://iot2050-rt.cfg"
