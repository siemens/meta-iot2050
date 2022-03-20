#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit initramfs

INITRAMFS_INSTALL += " \
    initramfs-etc-overlay-hook \
    initramfs-abrootfs-hook \
    "
