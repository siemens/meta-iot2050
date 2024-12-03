#
# Copyright (c) Siemens AG, 2018-2024
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

def get_extra_cfg(d):
    import re

    overrides = d.getVar('OVERRIDES')
    extra_cfg = ""

    if re.search("meta-hailo", overrides):
        extra_cfg += " file://iot2050_defconfig_hailo.cfg"

    return extra_cfg

SRC_URI += " \
    https://cdn.kernel.org/pub/linux/kernel/projects/cip/6.1/linux-cip-${PV}.tar.xz \
    ${@get_patches(d, 'patches-6.1')} \
    file://patches-6.1/ \
    file://${KERNEL_DEFCONFIG} \
    file://iot2050_defconfig_extra.cfg"
SRC_URI:append:pvu-dma = " \
    file://iot2050_defconfig_pvu.cfg \
    ${@get_extra_cfg(d)}"

S = "${WORKDIR}/linux-cip-${PV}"

KERNEL_DEFCONFIG = "iot2050_defconfig_base"
