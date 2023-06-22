#
# Copyright (c) Siemens AG, 2018-2023
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

SRC_URI[sha256sum] = "f45c47c9944c53920d483eb9b9be205e42c7d0af89f8c8c9bc0d3fb56a95e5c8"

SRC_URI += "file://iot2050-rt.cfg"
