#
# Copyright (c) Siemens AG, 2018-2022
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-kernel/linux/linux-custom.inc

def get_patches(d, patchdir):
    import glob

    files_dir = os.path.join(d.getVar('THISDIR'), 'files')
    patch_glob = os.path.join(files_dir, patchdir, '*.patch')
    patches = glob.glob(patch_glob)
    patches.sort()

    return ' '.join(['file://' + patch[len(files_dir)+1:] for patch in patches])

SRC_URI += " \
    https://gitlab.com/cip-project/cip-kernel/linux-cip/-/archive/v${PV}/linux-cip-v${PV}.tar.gz \
    ${@get_patches(d, 'patches-5.10')} \
    file://${KERNEL_DEFCONFIG} \
    file://iot2050_defconfig_extra.cfg"

S = "${WORKDIR}/linux-cip-v${PV}"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"
