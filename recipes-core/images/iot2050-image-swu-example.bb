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
require recipes-core/images/efibootguard.inc
require recipes-core/images/swupdate.inc

inherit image_uuid

IMAGE_TYPEDEP:wic += "squashfs"
IMAGE_TYPEDEP:wic:secureboot += "verity"

WKS_FILE = "iot2050-swu.wks.in"
WKS_FILE:secureboot = "iot2050-swu-secure.wks.in"

IMAGE_FSTYPES += "swu"
SWU_ROOTFS_TYPE:secureboot = "verity"

# watchdog is managed by U-Boot - disable
WDOG_TIMEOUT = "0"

INITRD_DEPLOY_FILE = "${INITRAMFS_RECIPE}-${DISTRO}-${MACHINE}.initrd.img"

# not compatible with SWUpdate images
IMAGE_INSTALL:remove = "regen-rootfs-uuid"
IMAGE_INSTALL:remove = "install-on-emmc"

# not compatible with disk encryption
IMAGE_INSTALL:remove:secureboot = "expand-on-first-boot"

# EFI Boot Guard is used instead
IMAGE_INSTALL:remove = "u-boot-script"

IMAGE_INSTALL += "customizations-swupdate"
IMAGE_INSTALL += "swupdate-handler-roundrobin"
IMAGE_INSTALL += "swupdate-complete-update-helper"
IMAGE_INSTALL += "${@ 'iot2050-watchdog' if d.getVar('QEMU_IMAGE') != '1' else '' }"

IMAGE_INSTALL:append:secureboot = " iot2050-efivarfs-helper"
