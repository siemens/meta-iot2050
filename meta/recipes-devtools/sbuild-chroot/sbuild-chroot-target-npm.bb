#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Felix Moessbauer <felix.moessbauer@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
PR = "1"
DESCRIPTION = "Isar sbuild/schroot filesystem for npm"

require recipes-devtools/sbuild-chroot/sbuild-chroot-target.bb

SBUILD_FLAVOR = "npm"
SBUILD_CHROOT_PREINSTALL_EXTRA += "npm python3 libnode115"
