#
# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

PR = "1"

inherit initramfs-hook

RDEPENDS += "initramfs-cip-functions"
DEBIAN_DEPENDS .= ", coreutils, util-linux, initramfs-cip-functions"
HOOK_ADD_MODULES = "efivarfs"

SRC_URI += " \
    file://local-top-complete"

HOOK_COPY_EXECS = "blkid dd tr"
