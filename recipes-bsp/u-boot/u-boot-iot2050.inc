#
# Copyright (c) Siemens AG, 2019-2020
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-bsp/u-boot/u-boot-custom.inc

SRC_URI += " \
    file://keys \
    file://prebuild \
    "

# Build environment
DEBIAN_BUILD_DEPENDS =. "openssl, libssl-dev:native, libssl-dev:arm64,"

do_prepare_build_append() {
    ln -sf ../keys ${S}
    echo "${SPI_FLASH_IMG} /usr/lib/u-boot/${MACHINE}" > \
        ${S}/debian/u-boot-${MACHINE}.install
    echo -$(${ISAR_RELEASE_CMD}) > ${S}/.scmversion
}

do_build[dirs] += "${DEPLOY_DIR_IMAGE}"

do_deploy() {
    cp -f "${S}/${SPI_FLASH_IMG}" "${DEPLOY_DIR_IMAGE}/${SPI_FLASH_DEPLOY_IMG}"
}

addtask deploy after do_dpkg_build before do_build
do_deploy[dirs] = "${DEPLOY_DIR_IMAGE}"
