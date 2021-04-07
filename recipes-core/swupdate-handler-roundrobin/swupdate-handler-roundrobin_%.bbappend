#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

DEPENDS += "patch-u-boot-env"
DEBIAN_DEPENDS += "patch-u-boot-env"

SRC_URI += "file://swupdate.handler.u-boot.ini"
