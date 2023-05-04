#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Torsten Hahn <torsten.hahn.extern@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

DESCRIPTION = "Commandline tool to read the state of the rtc battery"
MAINTAINER = "torsten.hahn.ext@siemens.com"

SRC_URI = "file://src"

S = "${WORKDIR}/src"

DEBIAN_BUILD_DEPENDS = "cmake"
DEBIAN_DEPENDS = "\${shlibs:Depends}"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize
}

# propably correct permissions 

