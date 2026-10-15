#!/bin/sh
#
# Copyright (c) Siemens AG, 2020-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Baocheng Su <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT

set -eu

ROOT_DEV="$(findmnt / -o source -n)"
BOOT_DEV="$(echo "${ROOT_DEV}" | sed 's/p\?[0-9]*$//')"

if [ "${ROOT_DEV}" = "${BOOT_DEV}" ]; then
	echo "Boot device equals root device - no partitioning found" >&2
	exit 1
fi

if ! sgdisk --randomize-guids "${BOOT_DEV}"; then
	echo "Failed to randomize PARTUUIDs on ${BOOT_DEV}." >&2
	exit 1
fi

sync
