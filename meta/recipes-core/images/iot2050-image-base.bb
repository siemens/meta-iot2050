#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
require recipes-core/images/meta-packages.inc

inherit image

DESCRIPTION = "IOT2050 Debian Base Image"

IMAGE_INSTALL += "${IOT2050_META_PACKAGES}"

# Make the .wic.img symlink to the .wic file for better backward compatibility
do_deploy() {
    echo "Linking wic img"
    ln -sf ${IMAGE_FULLNAME}.wic ${DEPLOY_DIR_IMAGE}/${IMAGE_FULLNAME}.wic.img
}
