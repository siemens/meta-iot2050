#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-devtools/secure-boot-secrets/secure-boot-secrets.inc

DESCRIPTION = "Add custMpk-based secrets to the buildchroot and the script to \
               sign an image with the given key"

SB_KEY = "custMpk.pem"
SB_CERT = "custMpk.crt"
