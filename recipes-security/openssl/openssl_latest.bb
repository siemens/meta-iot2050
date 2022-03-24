#
# Copyright (c) Siemens AG, 2020-2022
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
    file://0001-make-bnrand_range-reliable-with-deterministic-run-ti.patch;apply=no \
    "
CHANGELOG_V="<orig-version>+iot2050"

KEEP_INSTALLED_ON_CLEAN = "1"

DEB_BUILD_OPTIONS += "nocheck"

do_prepare_build() {
	deb_add_changelog

	cd ${S}
	quilt import ${WORKDIR}/*.patch
	quilt push -a
}
