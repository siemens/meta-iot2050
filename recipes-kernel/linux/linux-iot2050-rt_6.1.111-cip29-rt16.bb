#
# Copyright (c) Siemens AG, 2018-2024
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-6.1.inc

SRC_URI[sha256sum] = "486d7c3dc921101a9ec29e829b9d31dd0c1f46533591c7ace572cf201939e2cb"

SRC_URI += "file://iot2050-rt.cfg"
