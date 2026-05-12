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

SWU_HW_COMPAT = "IOT2050"

ABROOTFS_IMAGE_RECIPE ?= "iot2050-image-swu-example"
VERITY_IMAGE_RECIPE ?= "iot2050-image-swu-example"
INITRAMFS_RECIPE ?= "iot2050-initramfs"
ABROOTFS_PART_UUID_A ?= "fedcba98-7654-3210-cafe-5e0710000001"
ABROOTFS_PART_UUID_B ?= "fedcba98-7654-3210-cafe-5e0710000002"

IMAGE_INITRD = "${INITRAMFS_RECIPE}"
do_image_wic[depends] += "${INITRAMFS_RECIPE}:do_build"

# not compatible with SWUpdate images
IMAGE_INSTALL:remove = "install-on-emmc"

# not compatible with disk encryption
IMAGE_INSTALL:remove:secureboot = "expand-on-first-boot"

IMAGE_INSTALL += "swupdate-config-${MACHINE}"
IMAGE_INSTALL += "swupdate-handler-roundrobin"
IMAGE_INSTALL += "swupdate-complete-update-helper"
IMAGE_INSTALL += "${@ 'iot2050-watchdog' if d.getVar('QEMU_IMAGE') != '1' else '' }"

IMAGE_INSTALL:append:secureboot = " iot2050-efivarfs-helper"
