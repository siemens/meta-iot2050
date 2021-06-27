#!/bin/sh
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# SPDX-License-Identifier: MIT

LED_ORANGE="1 1"
LED_RED="0 1"
LED_GREEN="1 0"

turn_leds_off()
{
	echo 0 > /sys/class/leds/status-led-green/brightness
	echo 0 > /sys/class/leds/status-led-red/brightness
}

end_blinking()
{
	local PID=${BLINK_PID}

	if [ -n "${PID}" ]; then
		unset BLINK_PID
		kill ${PID}
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
		sleep $1
		kill -ALRM $$
	)&
	TIMER_PID=$!
}

timer_expired()
{
	echo "Timeout expired, skipping eMMC installation."
	kill ${GPIOMON_PID}
	exit 0
}

blink()
{
	(
		while true; do
			echo $1 > /sys/class/leds/status-led-green/brightness
			echo $2 > /sys/class/leds/status-led-red/brightness
			sleep $3;

			turn_leds_off
			sleep $3
		done
	)&
	BLINK_PID=$!
}

ROOT_DEV="$(findmnt / -o source -n)"
BOOT_DEV="$(echo "${ROOT_DEV}" | sed 's/p\?[0-9]*$//')"
EMMC_DEV="$(ls /dev/mmcblk*boot0 2>/dev/null | sed 's/boot0//')"

trap terminate 0

if [ -z "${EMMC_DEV}" ]; then
	echo "No eMMC found"
	exit 0
fi

if [ "${EMMC_DEV}" = "${BOOT_DEV}" ]; then
	echo "Already booting from eMMC"
	exit 0
fi

# Presence of /etc/install-on-emmc skips button check
if [ -e /etc/install-on-emmc ]; then
	echo "Found /etc/install-on-emmc, starting installation on eEMMC"
else
	echo "Press USER button to install on eMMC, you have 20 seconds"
	echo "WARNING: All data on eMMC will be overwritten!"
	GPIO_PIN=$(gpiofind USER-button)

	blink ${LED_ORANGE} 1

	trap timer_expired ALRM
	start_timer 20

	gpiomon -f -s -n 1 ${GPIO_PIN} &
	GPIOMON_PID=$!
	wait ${GPIOMON_PID}

	kill ${TIMER_PID}
	end_blinking

	blink ${LED_RED} 0.25

	echo "Hold USER button for 5 seconds to confirm"
	for N in $(seq 50); do
		if [ $(gpioget ${GPIO_PIN}) = 1 ]; then
			echo "Terminated - rebooting..."
			reboot
		fi
		sleep 0.1
	done

	end_blinking
fi

blink ${LED_GREEN} 0.25

# Calculate number of sectors to write:
# Start of boot partition + sectors in that partition
SECTORS="$(($(sfdisk -d ${BOOT_DEV} 2>/dev/null | tail -1 | sed 's/.*start=[[:space:]]*\([^,]*\), size=[[:space:]]*\([^,]*\).*/\1+\2/')))"

echo "Writing ${SECTORS} sectors to eMMC ${EMMC_DEV}..."
dd if=${BOOT_DEV} of=${EMMC_DEV} count=${SECTORS}
sync

echo "Updating partition UUID of eMMC rootfs"
partx -a ${EMMC_DEV}
udevadm settle
if ! test -b ${EMMC_DEV}p1; then
	echo "Waiting for ${EMMC_DEV}p1 to appear"
	while ! test -b ${EMMC_DEV}p1; do
		echo -n "."
		sleep 1
	done
fi
mount ${EMMC_DEV}p1 /mnt
mount -o bind /dev /mnt/dev
mount -t proc proc /mnt/proc
chroot /mnt sh -c ' \
    /usr/share/regen-rootfs-uuid/regen-rootfs-uuid.sh
    /bin/systemctl disable regen-rootfs-uuid-on-first-boot.service
    /bin/systemctl disable install-on-emmc-on-first-boot.service'
umount /mnt/dev /mnt/proc /mnt

reboot
