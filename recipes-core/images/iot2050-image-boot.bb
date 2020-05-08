#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
inherit image

DESCRIPTION = "IOT2050 Boot Image"

ISAR_RELEASE_CMD = "git -C ${LAYERDIR_meta-iot2050} describe --tags --dirty --match 'v[0-9].[0-9]*' --always || echo unknown"
# Only boot files
IMAGE_INSTALL = "u-boot-tools"
IMAGE_PREINSTALL = ""

do_copy_boot_files() {
}
