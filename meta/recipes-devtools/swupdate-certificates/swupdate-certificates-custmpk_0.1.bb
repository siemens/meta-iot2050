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

inherit iot2050-demo-signing-warning

SWU_SIGN_CERT = "custMpk.crt"
IOT2050_WARN_DEMO_SIGNING_KEYS = "1"

do_install[prefuncs] += "iot2050_warn_demo_signing_keys"

DEBIAN_CONFLICTS = "swupdate-certificates-snakeoil"
