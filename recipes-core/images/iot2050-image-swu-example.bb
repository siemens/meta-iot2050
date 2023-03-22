#
# Copyright (c) Siemens AG, 2021-2023
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-core/images/iot2050-image-example.bb
require recipes-core/images/swupdate.inc

inherit image_uuid

IMAGE_TYPEDEP:wic += "squashfs"
IMAGE_TYPEDEP:wic:secureboot += "verity"

WKS_FILE = "iot2050-swu.wks.in"
WKS_FILE:secureboot = "iot2050-swu-secure.wks.in"

IMAGE_FSTYPES += "swu"
SWU_ROOTFS_TYPE:secureboot = "verity"

WIC_IMAGER_INSTALL += "efibootguard"
# watchdog is managed by U-Boot - disable
WDOG_TIMEOUT = "0"
WICVARS += "WDOG_TIMEOUT KERNEL_IMAGE INITRD_IMAGE DTB_FILES"

# not compatible with SWUpdate images
IMAGE_INSTALL:remove = "regen-rootfs-uuid"
IMAGE_INSTALL:remove = "install-on-emmc"

# EFI Boot Guard is used instead
IMAGE_INSTALL:remove = "u-boot-script"

IMAGE_INSTALL += "efibootguard"
IMAGE_INSTALL += "swupdate"
IMAGE_INSTALL += "swupdate-handler-roundrobin"
IMAGE_INSTALL += "swupdate-complete-update-helper"
IMAGE_INSTALL += "iot2050-watchdog"

IMAGE_INSTALL:append:secureboot = " iot2050-efivarfs-helper"
