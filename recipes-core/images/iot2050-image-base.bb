#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit image

DESCRIPTION = "IOT2050 Debian Base Image"

IMAGE_INSTALL += "${@ 'u-boot-${MACHINE}-config' if d.getVar('QEMU_IMAGE') != '1' else '' }"
IMAGE_INSTALL += "iot2050-firmware"
IMAGE_INSTALL += "customizations-base"

IMAGE_PREINSTALL += "libubootenv-tool"

# Make the .wic.img symlink to the .wic file for better backward compatibility
do_deploy() {
    echo "Linking wic img"
    ln -sf ${IMAGE_FULLNAME}.wic ${DEPLOY_DIR_IMAGE}/${IMAGE_FULLNAME}.wic.img
}
