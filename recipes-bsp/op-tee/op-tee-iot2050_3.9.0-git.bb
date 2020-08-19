#
# Copyright (c) Siemens AG, 2020
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg

SRC_URI = " \
    git://github.com/OP-TEE/optee_os.git;protocol=https  \
    file://rules"
SRCREV = "50bbda3dd3b2397d27b5dd74a78567203821fa43"

DEBIAN_BUILD_DEPENDS = " \
    git, \
    python3-crypto:native, \
    python3-pycryptodome:native, \
    python3-pyelftools"

S = "${WORKDIR}/git"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize

    echo "out/arm-plat-k3/core/tee-pager_v2.bin /usr/lib/op-tee/iot2050/" > ${S}/debian/install
}
