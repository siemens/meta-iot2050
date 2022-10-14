#
# Copyright (c) Siemens AG, 2018-2022
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-5.10.inc

SRC_URI[sha256sum] = "a5598f7f673b3ef819d6ed24f08d539eecb6febd11673a1d4752a1c05d4ee289"

SRC_URI += "file://iot2050-rt.cfg"
