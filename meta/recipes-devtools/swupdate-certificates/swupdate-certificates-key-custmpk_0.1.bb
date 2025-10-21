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

DEPENDS += "swupdate-certificates"
DEBIAN_DEPENDS += "swupdate-certificates"

require recipes-devtools/swupdate-certificates/swupdate-certificates-key.inc

SWU_SIGN_KEY = "custMpk.pem"

DEBIAN_CONFLICTS = "swupdate-certificates-key-snakeoil"
