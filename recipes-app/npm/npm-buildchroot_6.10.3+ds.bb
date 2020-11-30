#
# Copyright (c) Siemens AG, 2019-2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-gbp

SRC_URI = "git://salsa.debian.org/freexian-team/npm.git;protocol=https"
SRCREV = "616a7c023dcb4d98cbb8502b0ce0b54e8997ae6b"

GBP_EXTRA_OPTIONS += "--git-compression=xz"

do_prepare_build() {
    sed -i "s/^Package: npm$/Package: npm-buildchroot\nConflicts: npm/" ${S}/debian/control
    sed -i "s|debian/npm\([ /]\)|debian/npm-buildchroot\1|" ${S}/debian/rules
}
