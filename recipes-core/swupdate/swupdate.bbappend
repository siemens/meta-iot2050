#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += "file://swupdate.install \
            file://swupdate.handler.uboot.ini"

do_prepare_build_append() {

    sed -i '/^local configuration =.*/i --[===[ EXAMPLE configuration:' ${S}/swupdate_handlers.lua
    sed -i '/^-- Default configuration .*/i --]===]' ${S}/swupdate_handlers.lua
    sed -i '/swupdate.set_bootenv(\"swupdate\", value)/a swupdate.set_bootenv(\"ustate\", 1)' ${S}/swupdate_handlers.lua

    cp ${WORKDIR}/swupdate.install ${S}/debian/swupdate.install
    cp ${WORKDIR}/swupdate.handler.uboot.ini ${S}/swupdate.handler.ini
}
