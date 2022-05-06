#
# Copyright (c) Siemens AG, 2021-2022
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

IMAGE_UUID = "image_uuid"
IMAGE_UUID_secureboot = ""

inherit ${IMAGE_UUID}

# generate a swu image for a/b updating via swupdate
IMAGE_FSTYPES = "wic-swu-img"
IMAGE_FSTYPES_secureboot = "secure-wic-swu-img"

require recipes-core/images/swupdate.inc
require recipes-core/images/iot2050-image-example.bb

WKS_FILE = "iot2050-swu.wks.in"
WKS_FILE_secureboot = "iot2050-swu-secure.wks.in"

WIC_IMAGER_INSTALL += "efibootguard"
# watchdog is managed by U-Boot - disable
WDOG_TIMEOUT = "0"
WICVARS += "WDOG_TIMEOUT KERNEL_IMAGE INITRD_IMAGE DTB_FILES"

# not compatible with SWUpdate images
IMAGE_INSTALL_remove = "regen-rootfs-uuid"
IMAGE_INSTALL_remove = "install-on-emmc"
IMAGE_INSTALL_remove = "node-red-preinstalled-nodes"

# EFI Boot Guard is used instead
IMAGE_INSTALL_remove = "u-boot-script"

IMAGE_INSTALL += "efibootguard"
IMAGE_INSTALL += "swupdate"
IMAGE_INSTALL += "swupdate-handler-roundrobin"
IMAGE_INSTALL += "swupdate-complete-update-helper"
IMAGE_INSTALL += "iot2050-watchdog"
