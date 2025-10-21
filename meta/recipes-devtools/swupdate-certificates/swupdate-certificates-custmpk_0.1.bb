#
# CIP Core, generic profile
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT
#

require recipes-devtools/swupdate-certificates/swupdate-certificates.inc

SWU_SIGN_CERT = "custMpk.crt"

DEBIAN_CONFLICTS = "swupdate-certificates-snakeoil"
