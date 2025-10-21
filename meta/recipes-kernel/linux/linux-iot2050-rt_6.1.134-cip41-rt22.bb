#
# Copyright (c) Siemens AG, 2018-2024
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require linux-iot2050-6.1.inc

PR = "1"

SRC_URI[sha256sum] = "8582da7b30925237cf4905988aefe0a8de23bb4e7546e6ebb998419ee121fa7e"

SRC_URI += "file://iot2050-rt.cfg"
