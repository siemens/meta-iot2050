#
# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

PR = "1"

require recipes-initramfs/iot2050-initramfs/iot2050-initramfs_0.1.bb

INITRAMFS_INSTALL:remove:secureboot = " \
	initramfs-verity-hook \
	initramfs-crypt-hook \
	initramfs-tee-supplicant-hook \
	initramfs-tee-ftpm-hook \
	"

INITRAMFS_INSTALL += " initramfs-efi-rootfs-hook"
