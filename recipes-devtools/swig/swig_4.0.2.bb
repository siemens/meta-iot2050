#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

SRC_URI = " \
    apt://${PN} \
    file://0001-Introduce-macros-to-support-both-Handle-and-Local-ty.patch;apply=no \
    file://0002-Replace-Handle-with-Local-depending-on-Node.js-versi.patch;apply=no \
    file://0003-Add-support-for-Node.js-v12.patch;apply=no \
    file://0004-Fixes-for-node-v12.0-12.5.patch;apply=no"

PACKAGE_ARCH = "${HOST_ARCH}"

CHANGELOG_V = "<orig-version>+isar"

do_prepare_build() {
    deb_add_changelog

    cd ${S}
    quilt import ${WORKDIR}/*.patch
    quilt push -a
}
