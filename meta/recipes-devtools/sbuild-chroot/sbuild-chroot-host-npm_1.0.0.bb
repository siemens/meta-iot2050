#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
PR = "1"
DESCRIPTION = "Isar sbuild/schroot filesystem for npm on host"

require recipes-devtools/sbuild-chroot/sbuild-chroot-host.bb

SBUILD_FLAVOR = "npm"
SBUILD_CHROOT_PREINSTALL_EXTRA += "npm python3 libnode115"
