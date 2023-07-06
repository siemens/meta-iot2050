#!/bin/sh
#
# This script is derived from isar-cip-core
# repository for meta-iot2050.
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Enes Colpan <enes.colpan@siemens.com>
#
# SPDX-License-Identifier: MIT
#

DISTRO_RELEASE="iot2050-debian"
MACHINE="iot2050-qemu"

usage()
{
	echo "Usage: $0 [QEMU_OPTIONS]"
	echo
	echo "The architecture defaults to the setting in .config.yaml and can be left out"
	echo "if the built was done via \"kas-container menu\"."
	echo
	echo "Environment variables (default to settings in .config.yaml):"
	echo "  QEMU_PATH         use a locally built QEMU version"
	echo "  IMAGE_SWUPDATE    boot swupdate image"
	echo "  IMAGE_EXAMPLE     boot example image"
	exit 1
}

if grep -s -q "IMAGE_QEMU: false" .config.yaml; then
	echo "Please select IMAGE_QEMU and rebuild image. The current image is not compatible with QEMU!"
	usage
fi

QEMU=qemu-system-aarch64
QEMU_COMMON_OPTIONS=" \
	-cpu cortex-a53 \
	-smp 4 \
	-m 2G \
	-serial mon:stdio \
	-netdev user,id=net,hostfwd=tcp:127.0.0.1:22222-:22 \
	-machine virt \
	-device virtio-serial-device \
	-device virtconsole,chardev=con -chardev vc,id=con \
	-device virtio-blk-device,drive=disk \
	-device virtio-net-device,netdev=net"
KERNEL_CMDLINE=" \
	root=/dev/vda1 rw"

if grep -s -q "IMAGE_EXAMPLE: true" .config.yaml; then
	TARGET_IMAGE="iot2050-image-example"
elif grep -s -q "IMAGE_SWUPDATE: true" .config.yaml; then
	SWUPDATE_BOOT="true"
	TARGET_IMAGE="iot2050-image-swu-example"
fi

BASE_DIR=$(readlink -f $(dirname $0))
IMAGE_PREFIX="${BASE_DIR}/build/tmp/deploy/images/${MACHINE}/${TARGET_IMAGE}-${DISTRO_RELEASE}-${MACHINE}"

if [ -n "${SWUPDATE_BOOT}" ]; then

	u_boot_bin=${FIRMWARE_BIN:-./build/tmp/deploy/images/${MACHINE}/firmware.bin}

	${QEMU_PATH}${QEMU} \
		-drive file=${IMAGE_PREFIX}.wic,discard=unmap,if=none,id=disk,format=raw \
		-bios ${u_boot_bin} \
		${QEMU_COMMON_OPTIONS} ${QEMU_EXTRA_ARGS} "$@"

else
	IMAGE_FILE=$(ls ${IMAGE_PREFIX}.wic)

	KERNEL_FILE=$(ls ${IMAGE_PREFIX}-vmlinu* | tail -1)
	INITRD_FILE=$(ls ${IMAGE_PREFIX}-initrd.img* | tail -1)

	${QEMU_PATH}${QEMU} \
		-drive file=${IMAGE_FILE},discard=unmap,if=none,id=disk,format=raw \
		-kernel ${KERNEL_FILE} -append "${KERNEL_CMDLINE}" \
		-initrd ${INITRD_FILE} \
		${QEMU_COMMON_OPTIONS} "$@"
fi
