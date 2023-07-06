#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit image

DESCRIPTION = "IOT2050 Debian Base Image"

IMAGE_INSTALL += "${@ 'u-boot-${MACHINE}-config' if d.getVar('QEMU_IMAGE') != '1' else '' }"
IMAGE_INSTALL += "iot2050-firmware"
IMAGE_INSTALL += "customizations-base"

IMAGE_PREINSTALL += "libubootenv-tool"

python aggregate_mainline_apt_sources () {
    import shutil

    aggregated_sources_fp = '%s/bootstrap.list' % d.getVar("WORKDIR", True)
    raw_apt_sources_list = d.getVar("DISTRO_APT_SOURCES_MAINLINE_LIST", True) or ""
    apt_sources_list = raw_apt_sources_list.strip().split()

    if len(apt_sources_list) == 0:
        bb.fatal("Cannot parse DISTRO_APT_SOURCES_MAINLINE_LIST: %s" % 
            raw_apt_sources_list)

    with open(aggregated_sources_fp, "wb") as out_fd:
        for entry in apt_sources_list:
            entry_real = bb.parse.resolve_file(entry, d)
            with open(entry_real, "rb") as in_fd:
                shutil.copyfileobj(in_fd, out_fd, 1024*1024*10)
            out_fd.write("\n".encode())
}

install_mainline_sources_list () {
    sudo rm -f '${IMAGE_ROOTFS}/etc/apt/sources-list'
    sudo install -m 644 '${WORKDIR}/bootstrap.list' '${IMAGE_ROOTFS}/etc/apt/sources-list'
    sudo rm -f '${WORKDIR}/bootstrap.list'
}

# For rootfs build using debian snapshot packages, restore the source list file
# with the mainline sources list, so that users can update packages via 
# `apt update`.
# TODO: this code should be merged to ISAR.
ROOTFS_POSTPROCESS_COMMAND =+ "image_postprocess_restore_sources_list"
python image_postprocess_restore_sources_list () {
    pkg_selection = d.getVar("PACKAGES_SELECTION", True) or ""
    if pkg_selection == 'packages-snapshot':
        bb.build.exec_func("aggregate_mainline_apt_sources", d)
        bb.build.exec_func("install_mainline_sources_list", d)
    else:
        bb.note('No need to restore sources for mainline packages')
}

# Make the .wic.img symlink to the .wic file for better backward compatibility
do_deploy() {
    echo "Linking wic img"
    ln -sf ${IMAGE_FULLNAME}.wic ${DEPLOY_DIR_IMAGE}/${IMAGE_FULLNAME}.wic.img
}
