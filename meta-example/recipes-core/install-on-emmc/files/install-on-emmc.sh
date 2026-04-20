#!/bin/sh
#
# Copyright (c) Siemens AG, 2021-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

LED_ORANGE="1 1"
LED_RED="0 1"
LED_GREEN="1 0"

run_probe()
{
	"$@" 2>/dev/null
}

kill_if_running()
{
	PID="$1"

	[ -n "${PID}" ] || return 0
	kill "${PID}" 2>/dev/null || true
}

umount_if_mounted()
{
	TARGET="$1"

	[ -n "${TARGET}" ] || return 0
	umount "${TARGET}" 2>/dev/null || true
}

turn_leds_off()
{
	echo 0 > /sys/class/leds/status-led-green/brightness
	echo 0 > /sys/class/leds/status-led-red/brightness
}

end_blinking()
{
	PID=${BLINK_PID}

	if [ -n "${PID}" ]; then
		unset BLINK_PID
		kill_if_running "${PID}"
		turn_leds_off
	fi
}

terminate()
{
	end_blinking

	mount -o remount,rw /
	systemctl disable install-on-emmc-on-first-boot.service
}

start_timer()
{
	(
		sleep "$1"
		kill -ALRM $$
	)&
	TIMER_PID=$!
}

timer_expired()
{
	echo "Timeout expired, skipping eMMC installation."
	kill_if_running "${GPIOMON_PID}"
	exit 0
}

blink()
{
	COLOR="$1"
	INTERVAL="$2"
	GREEN_STATE="${COLOR%% *}"
	RED_STATE="${COLOR#* }"

	(
		while true; do
			echo "${GREEN_STATE}" > /sys/class/leds/status-led-green/brightness
			echo "${RED_STATE}" > /sys/class/leds/status-led-red/brightness
			sleep "${INTERVAL}"

			turn_leds_off
			sleep "${INTERVAL}"
		done
	)&
	BLINK_PID=$!
}

find_emmc_device()
{
	for BOOT_PART in /dev/mmcblk*boot0; do
		[ -b "${BOOT_PART}" ] || continue
		printf '%s\n' "${BOOT_PART%boot0}"
		return 0
	done

	return 1
}

find_part_by_label()
{
	DEVICE="$1"
	LABEL="$2"

	for PART in "${DEVICE}"p*; do
		[ -b "${PART}" ] || continue
		if [ "$(lsblk -nro PARTLABEL "${PART}" 2>/dev/null)" = "${LABEL}" ]; then
			echo "${PART}"
			return 0
		fi
	done

	return 1
}

part_suffix()
{
	PART="$1"
	DEVICE="$2"

	case "${PART}" in
	${DEVICE}p*)
		printf '%s\n' "${PART#"${DEVICE}"p}"
		return 0
		;;
	esac

	return 1
}

cleanup_target_rootfs_mounts()
{
	umount_if_mounted /mnt/dev
	umount_if_mounted /mnt/proc
	umount_if_mounted /mnt
}

finalize_target_rootfs()
{
	TARGET_ROOT="$1"

	mkdir -p /mnt /mnt/dev /mnt/proc
	mount "${TARGET_ROOT}" /mnt || return 1
	mount -o bind /dev /mnt/dev || {
		cleanup_target_rootfs_mounts
		return 1
	}
	mount -t proc proc /mnt/proc || {
		cleanup_target_rootfs_mounts
		return 1
	}
	chroot /mnt sh -c ' \
		if [ -x /usr/share/regen-rootfs-uuid/regen-rootfs-uuid.sh ]; then
			/usr/share/regen-rootfs-uuid/regen-rootfs-uuid.sh
			/bin/systemctl disable regen-rootfs-uuid-on-first-boot.service || true
		fi
		/bin/systemctl disable install-on-emmc-on-first-boot.service || true' || {
		cleanup_target_rootfs_mounts
		return 1
	}
	cleanup_target_rootfs_mounts
}

wait_for_block_device()
{
	DEVICE="$1"
	TIMEOUT="$2"

	for _ in $(seq "${TIMEOUT}"); do
		if test -b "${DEVICE}"; then
			return 0
		fi
		sleep 1
	done

	return 1
}

ROOT_DEV="$(findmnt / -o source -n)"
BOOT_DEV="$(echo "${ROOT_DEV}" | sed 's/p\?[0-9]*$//')"
EMMC_DEV="$(find_emmc_device || true)"
SFDISK_DUMP="$(sfdisk -d "${BOOT_DEV}" 2>/dev/null || true)"
SOURCE_ROOT_PART="$(find_part_by_label "${BOOT_DEV}" rootfs || true)"

if [ -z "${SOURCE_ROOT_PART}" ]; then
	SOURCE_ROOT_PART="$(printf '%s\n' "${SFDISK_DUMP}" | awk -F: '/^\/dev\// { part=$1 } END { gsub(/^[[:space:]]+|[[:space:]]+$/, "", part); print part }')"
fi

SOURCE_ROOT_ENTRY="$(printf '%s\n' "${SFDISK_DUMP}" | awk -F: -v part="${SOURCE_ROOT_PART}" '{ name=$1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", name) } name == part { print; exit }')"

TARGET_ROOT_SUFFIX="$(part_suffix "${SOURCE_ROOT_PART}" "${BOOT_DEV}" || true)"
TARGET_ROOT_PART="${EMMC_DEV}p${TARGET_ROOT_SUFFIX}"

trap terminate 0

if [ -z "${EMMC_DEV}" ]; then
	echo "No eMMC found"
	exit 0
fi

if [ "${EMMC_DEV}" = "${BOOT_DEV}" ]; then
	echo "Already booting from eMMC"
	exit 0
fi

if [ -z "${TARGET_ROOT_SUFFIX}" ]; then
	echo "Could not determine the rootfs partition number on ${BOOT_DEV}." >&2
	exit 1
fi

# Presence of /etc/install-on-emmc skips button check
if [ -e /etc/install-on-emmc ]; then
	echo "Found /etc/install-on-emmc, starting installation on eMMC"
else
	echo "Press USER button to install on eMMC, you have 20 seconds"
	echo "WARNING: All data on eMMC will be overwritten!"
	GPIO_PIN="USER-button"

	blink "${LED_ORANGE}" 1

	trap timer_expired ALRM
	start_timer 20

	gpiomon -e falling -q -n 1 "${GPIO_PIN}" &
	GPIOMON_PID=$!
	wait "${GPIOMON_PID}"

	kill_if_running "${TIMER_PID}"
	end_blinking

	blink "${LED_RED}" 0.25

	echo "Hold USER button for 5 seconds to confirm"
	for _ in $(seq 50); do
		if [ "$(gpioget --numeric "${GPIO_PIN}")" = 1 ]; then
			echo "Terminated - rebooting..."
			reboot
		fi
		sleep 0.1
	done

	end_blinking
fi

blink "${LED_GREEN}" 0.25

IS_GPT="$(printf '%s\n' "${SFDISK_DUMP}" | grep -q 'label: gpt' && echo 1 || echo 0)"

# Calculate the number of sectors to copy up to the end of the source rootfs
# partition.
SOURCE_ROOT_START="$(printf '%s\n' "${SOURCE_ROOT_ENTRY}" | sed -n 's/.*start=[[:space:]]*\([^,]*\), size=.*/\1/p')"
SOURCE_ROOT_SIZE="$(printf '%s\n' "${SOURCE_ROOT_ENTRY}" | sed -n 's/.*size=[[:space:]]*\([^,]*\).*/\1/p')"

if [ -z "${SOURCE_ROOT_ENTRY}" ] || [ -z "${SOURCE_ROOT_START}" ] || [ -z "${SOURCE_ROOT_SIZE}" ]; then
	echo "Could not determine copy size from ${SOURCE_ROOT_PART}." >&2
	exit 1
fi

SECTORS="$((SOURCE_ROOT_START + SOURCE_ROOT_SIZE))"
COPY_BYTES="$((SECTORS * 512))"

echo "Copying $((COPY_BYTES / 1024 / 1024)) MiB to eMMC ${EMMC_DEV}..."
# With iflag=count_bytes, dd interprets count as bytes rather than bs-sized blocks.
dd if="${BOOT_DEV}" of="${EMMC_DEV}" bs=4M count="${COPY_BYTES}" iflag=count_bytes,fullblock conv=fsync status=progress

if [ "${IS_GPT}" = "1" ]; then
	echo "Recreating GPT on ${EMMC_DEV}..."
	sfdisk -d "${BOOT_DEV}" 2>/dev/null | \
		grep -v last-lba | \
		sfdisk --force "${EMMC_DEV}"
fi

sync

echo "Waiting for ${TARGET_ROOT_PART} to appear on ${EMMC_DEV}..."
run_probe partx -u "${EMMC_DEV}" || run_probe partx -a "${EMMC_DEV}" || true
run_probe udevadm settle --timeout=10 --exit-if-exists="${TARGET_ROOT_PART}" || \
	run_probe udevadm settle --timeout=10 || true

if ! wait_for_block_device "${TARGET_ROOT_PART}" 30; then
	echo "Timed out waiting for ${TARGET_ROOT_PART}." >&2
	echo "The eMMC copy may be incomplete or the partition table was not accepted." >&2
	exit 1
fi

TARGET_ROOT_BY_LABEL="$(find_part_by_label "${EMMC_DEV}" rootfs || true)"
if [ -n "${TARGET_ROOT_BY_LABEL}" ] && [ "${TARGET_ROOT_BY_LABEL}" != "${TARGET_ROOT_PART}" ]; then
	echo "Resolved rootfs label on ${EMMC_DEV} as ${TARGET_ROOT_BY_LABEL}, expected ${TARGET_ROOT_PART}." >&2
	echo "Using ${TARGET_ROOT_BY_LABEL}." >&2
	TARGET_ROOT_PART="${TARGET_ROOT_BY_LABEL}"
fi

echo "Finalizing copied system on ${TARGET_ROOT_PART}"
if ! finalize_target_rootfs "${TARGET_ROOT_PART}"; then
	echo "Failed to finalize copied system on ${TARGET_ROOT_PART}." >&2
	exit 1
fi

reboot
