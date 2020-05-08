# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# SPDX-License-Identifier: MIT

BOOT_IMG_SIZE_KB ?= "8192"
BOOT_IMG_FILE = "${DEPLOY_DIR_IMAGE}/${IMAGE_FULLNAME}.bin"

do_boot_img[stamp-extra-info] = "${DISTRO}-${MACHINE}"

do_boot_flash_img() {
    rm -f ${BOOT_IMG_FILE}
    dd if=/dev/zero ibs=1k count=${BOOT_IMG_SIZE_KB} | tr "\000" "\377" > ${BOOT_IMG_FILE}
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/tiboot3.bin of=${BOOT_IMG_FILE} seek=0 oflag=seek_bytes conv=notrunc
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/tispl.bin of=${BOOT_IMG_FILE} seek=512K oflag=seek_bytes conv=notrunc
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/u-boot.img of=${BOOT_IMG_FILE} seek=2560K oflag=seek_bytes conv=notrunc
    # Env
    dd if=/dev/zero ibs=1k count=128 of=${BOOT_IMG_FILE} seek=6656K oflag=seek_bytes conv=notrunc
    # Env.bak
    dd if=/dev/zero ibs=1k count=128 of=${BOOT_IMG_FILE} seek=6784K oflag=seek_bytes conv=notrunc
    # SysFW
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/sysfw.itb of=${BOOT_IMG_FILE} seek=6912K oflag=seek_bytes conv=notrunc
    # PRU ethernet FW
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/am65x-pru0-prueth-fw.elf of=${BOOT_IMG_FILE} seek=7936K oflag=seek_bytes conv=notrunc
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/am65x-pru1-prueth-fw.elf of=${BOOT_IMG_FILE} seek=8000K oflag=seek_bytes conv=notrunc
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/am65x-rtu0-prueth-fw.elf of=${BOOT_IMG_FILE} seek=8064K oflag=seek_bytes conv=notrunc
    dd if=${BUILDCHROOT_DIR}/usr/lib/u-boot/${MACHINE}/am65x-rtu1-prueth-fw.elf of=${BOOT_IMG_FILE} seek=8128K oflag=seek_bytes conv=notrunc
}

addtask boot_flash_img before do_build after do_copy_boot_files
