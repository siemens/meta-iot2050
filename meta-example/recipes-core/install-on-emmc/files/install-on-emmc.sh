#!/bin/sh
#
# Copyright (c) Siemens AG, 2021-2026
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#  Baocheng Su <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT

LED_ORANGE="1 1"
LED_RED="0 1"
LED_GREEN="1 0"
COPIER_MODE=0

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
		kill "${PID}"
		wait "${PID}" 2>/dev/null
		turn_leds_off
	fi
}

terminate()
{
	end_blinking

	mount -o remount,rw /
	systemctl disable install-on-emmc-on-first-boot.service
}

stay_on_result()
{
	end_blinking
	if [ "$1" -eq 0 ]; then
		echo "eMMC installation complete. Disconnect power and remove the installation medium before powering on."
		echo 0 > /sys/class/leds/status-led-red/brightness
		echo 1 > /sys/class/leds/status-led-green/brightness
	else
		echo "eMMC installation failed. Disconnect power before retrying." >&2
		echo 0 > /sys/class/leds/status-led-green/brightness
		echo 1 > /sys/class/leds/status-led-red/brightness
	fi
	# Keep systemd-remount-fs blocked until power is disconnected.
	while true; do
		sleep 3600
	done
}

on_exit()
{
	STATUS=$?
	trap - 0
	if [ "${COPIER_MODE}" -eq 1 ]; then
		stay_on_result "${STATUS}"
	else
		terminate
	fi
	exit "${STATUS}"
}

reboot_after_cleanup()
{
	terminate
	trap - 0
	sync
	reboot
	exit $?
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
	kill "${GPIOMON_PID}"
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

ROOT_DEV="$(findmnt / -o source -n)"
BOOT_DEV="$(echo "${ROOT_DEV}" | sed 's/p\?[0-9]*$//')"
EMMC_DEV="$(ls /dev/mmcblk*boot0 2>/dev/null | sed 's/boot0//')"

trap on_exit 0

if [ "${EMMC_DEV}" = "${BOOT_DEV}" ]; then
	echo "Already booting from eMMC"
	exit 0
fi

if [ -e /etc/install-on-emmc ]; then
	COPIER_MODE=1
fi

if [ -z "${EMMC_DEV}" ]; then
	echo "No eMMC found"
	exit "${COPIER_MODE}"
fi

# Presence of /etc/install-on-emmc skips button check
if [ "${COPIER_MODE}" -eq 1 ]; then
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

	kill "${TIMER_PID}"
	end_blinking

	blink "${LED_RED}" 0.25

	echo "Hold USER button for 5 seconds to confirm"
	for _ in $(seq 50); do
		if [ "$(gpioget --numeric "${GPIO_PIN}")" = 1 ]; then
			echo "Terminated - rebooting..."
			reboot_after_cleanup
		fi
		sleep 0.1
	done

	end_blinking
fi

blink "${LED_GREEN}" 0.25

SFDISK_JSON="$(sfdisk -J "${BOOT_DEV}" 2>/dev/null)" || {
	echo "Could not read partition table from ${BOOT_DEV}." >&2
	exit 1
}
SECTOR_SIZE="$(printf '%s\n' "${SFDISK_JSON}" | jq -er '.partitiontable.sectorsize')" || exit 1
SOURCE_PARTITION_END="$(printf '%s\n' "${SFDISK_JSON}" | jq -er '.partitiontable.partitions[-1] | .start + .size')" || exit 1

# Calculate the copy length through the end of the last source partition.
COPY_BYTES="$((SOURCE_PARTITION_END * SECTOR_SIZE))"

# Reserve space for backup GPT using the source's pre-partition metadata area.
GPT_RESERVED_SECTORS="$(printf '%s\n' "${SFDISK_JSON}" | jq -er '.partitiontable.firstlba')" || exit 1
REQUIRED_BYTES="$((COPY_BYTES + GPT_RESERVED_SECTORS * SECTOR_SIZE))"
EMMC_BYTES="$(blockdev --getsize64 "${EMMC_DEV}")" || exit 1
if [ "${EMMC_BYTES}" -lt "${REQUIRED_BYTES}" ]; then
	echo "Not enough space on ${EMMC_DEV}: ${REQUIRED_BYTES} bytes required, ${EMMC_BYTES} bytes available." >&2
	exit 1
fi

# Keep the source filesystem stable throughout the raw disk copy.
if ! mount -o remount,ro /; then
	echo "Could not remount source root filesystem read-only, aborting eMMC installation." >&2
	exit 1
fi

echo "Copying $((COPY_BYTES / 1024 / 1024)) MiB to eMMC ${EMMC_DEV}..."
# With iflag=count_bytes, dd interprets count as bytes rather than bs-sized blocks.
if ! dd if="${BOOT_DEV}" of="${EMMC_DEV}" bs=4M count="${COPY_BYTES}" iflag=count_bytes,fullblock conv=fsync status=progress; then
	echo "Failed to copy ${BOOT_DEV} to ${EMMC_DEV}, aborting eMMC installation." >&2
	exit 1
fi

echo "Relocating backup GPT to the end of ${EMMC_DEV}..."
sfdisk --relocate gpt-bak-std "${EMMC_DEV}" || exit 1

echo "Randomizing disk and partition GUIDs on ${EMMC_DEV}..."
sgdisk --randomize-guids "${EMMC_DEV}" || exit 1

sync || exit 1
if [ "${COPIER_MODE}" -eq 1 ]; then
	exit 0
fi
reboot_after_cleanup
