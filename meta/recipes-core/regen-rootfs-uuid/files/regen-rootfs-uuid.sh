#!/bin/sh
#
# Copyright (c) Siemens AG, 2020-2022
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# SPDX-License-Identifier: MIT

ROOT_DEV="$(findmnt / -o source -n)"
BOOT_DEV="$(echo "${ROOT_DEV}" | sed 's/p\?[0-9]*$//')"
ROOT_PART="$(echo "${ROOT_DEV}" | sed 's/.*[^0-9]\([0-9]*\)$/\1/')"

if [ "${ROOT_DEV}" = "${BOOT_DEV}" ]; then
	echo "Boot device equals root device - no partitioning found" >&2
	exit 1
fi

NEW_UUID=$(uuidgen)

sfdisk --part-uuid ${BOOT_DEV} ${ROOT_PART} ${NEW_UUID}

sed -i 's/PARTUUID=[^ ]*/PARTUUID='${NEW_UUID}'/i' /etc/default/u-boot-script

update-u-boot-script
sync
