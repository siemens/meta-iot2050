#
# Copyright (c) Siemens AG, 2018-2022
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

SRC_URI[sha256sum] = "5455a0270bc098c82ee6a9b759db9fe1fb4f43a5fa9c8275bf129dbe2c38c91c"

SRC_URI += "file://iot2050-rt.cfg"
