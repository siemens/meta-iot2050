#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg

SRC_URI = " \
    apt://${PN}/${BASE_DISTRO_CODENAME} \
    file://0001-shared-watchdog-Account-for-watchdogs-that-do-not-su.patch;apply=no \
    "
CHANGELOG_V="<orig-version>+iot2050"

KEEP_INSTALLED_ON_CLEAN = "1"

do_prepare_build() {
	deb_add_changelog

	cd ${S}
	quilt import ${WORKDIR}/*.patch
	quilt push -a

	# fix cross-build issue (see also https://salsa.debian.org/systemd-team/systemd/-/merge_requests/130)
	sed -i 's/python3-pyparsing /python3-pyparsing:native /' ${S}/debian/control
	sed -i 's/python3-evdev /python3-evdev:native /' ${S}/debian/control
}
