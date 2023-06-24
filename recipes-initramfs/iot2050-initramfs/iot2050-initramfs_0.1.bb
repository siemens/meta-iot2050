#
# Copyright (c) Siemens AG, 2022-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit initramfs

INITRAMFS_INSTALL += " \
    initramfs-overlay-hook \
    initramfs-abrootfs-hook \
    "

INITRAMFS_INSTALL:append:secureboot = " \
    initramfs-verity-hook \
    initramfs-crypt-hook \
    initramfs-tee-supplicant-hook \
    initramfs-tee-ftpm-hook \
    "
INITRAMFS_INSTALL:remove:secureboot = "initramfs-abrootfs-hook"
