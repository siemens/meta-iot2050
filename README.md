# META-IOT2050

This [Isar](https://github.com/ilbers/isar) layer contains recipes,
configuration and other artifacts that are specific to  Debian-based IOT2050
product.

## Build example image

Before building the system, you will need to install docker on build host. For
example under Debian Linux

```shell
sudo apt install docker.io
```

If you want to run docker as non-root user then you need to add your user to the
docker group:

```shell
sudo usermod -aG docker $USER
```

You may need to re-login or issue newgrp.

Then open the menu to select the desired image and options:

```shell
./kas-container menu
```

After the build completed, the final image is under

```text
build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic
```

## Build user SDK
>>>
**Note:** Current SDK only supports Linux x86-64 host machine
>>>

```shell
./kas-container build kas-iot2050-example.yml:kas/opt/sdk.yml
```
(or select SDK in `kas menu`)

After the build completed, the SDK tarball is located at

```text
build/tmp/deploy/images/iot2050/sdk-isar-arm64.tar.xz
```

Please follow the further instruction file `README.sdk` in the SDK tarball.

The SDK is also available as docker image. To import it into a docker host, run

```shell
docker load -i build/tmp/deploy/images/iot2050/sdk-iot2050-debian-arm64-docker-archive.tar.xz
```

## Build qemu image

To boot IOT2050 image from qemu, you need a customized image for proper booting.
Please use kas menu with the following command and select qemu image for target build
with example image or example image with swupdate support

```shell
./kas-container menu
```

Then below command can be used to boot qemu image on a platform that
qemu-system-aarch64 is installed.

Run qemu:
```shell
/bin/sh start-qemu-iot2050.sh"
```

## Clean build result

```shell
./kas-container --isar clean
```

## Booting the image from SD card

Under Linux, insert an unused SD card. Assuming the SD card takes device
/dev/mmcblk0, use dd to copy the image to it. For example:

```shell
$ sudo dd if=build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic \
          of=/dev/mmcblk0 bs=4M oflag=sync
```

Alternatively, install the bmap-tools package and run the following command
which is generally faster and safer:

```shell
$ sudo bmaptool copy build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic /dev/mmcblk0
```

The example image starts with the IP 192.168.200.1 preconfigured on the first
Ethernet interface, and use DHCP at another. You can use ssh to connect to the
system.

The BSP image does not configure the network. If you want to ssh into the
system, you can use the root terminal via UART to ifconfig the IP address and
use that to ssh in.

NOTE: To login, the default username and password is `root`. And you are
required to change the default password when first login.

## Installing the image on the eMMC (IOT2050 Advanced only)

During the very first boot of the image from an SD card or USB stick, you can
request the installation to the eMMC. For that, press the USER button while
the status LED is blinking orange during that first boot. Hold the button for
at least 5 seconds to start the installation.

NOTE: All content of the eMMC will be overwritten by this procedure!

The ongoing installation is signaled by a fast blinking status LED. Wait for
several minutes until the LED stops blinking and the device reboots to the eMMC.
You can safely remove the SD card or USB stick at that point.

The installation can also be triggered automatically by creating the file
`/etc/install-on-emmc` on the vanilla image by mounting it under Linux and
executing, e.g., `touch <mountpoint>/etc/install-on-emmc`.

## Selecting a boot device

By default, the boot loader will pick the first bootable device. If that device
may no longer fully start, you can select an alternative boot device in the
U-Boot shell. Attach a USB-UART adapter to X14, connect it to a host PC and open
a terminal program on that port. Reset the device and interrupt the boot when it
counts down ("Hit any key to stop autoboot"). Then type

```shell
=> setenv boot_targets mmc0
=> run distro_bootcmd
```

to boot from the microSD card. Use `usb0` for the first USB mass storage device.

NOTE: This selection is not persistent. The boot loader will fall back to its
default boot order after reset.

## Building with SWUpdate support

It is possible to create an image with a SWUpdate based [double copy
root file
system](https://sbabic.github.io/swupdate/overview.html#double-copy-with-fall-back)
for Over-The-Air updates by selecting the option `Example image with
SWUpdate support` during the image configuration with `./kas-container
menu`. You can also build the image by calling:

```shell
./kas-container build kas-iot2050-example.yml:kas/opt/swupdate-example.yml
```

You can find the final image under
`build/tmp/deploy/images/iot2050/iot2050-image-swu-example-iot2050-debian-iot2050.wic`.
This image holds the necessary partition layout with two root file
systems. The image
`iot2050-image-swu-example-iot2050-debian-iot2050.wic` can be flashed
directly to a SD card as described in section [Booting the image from SD
card](#booting-the-image-from-sd-card).

NOTE: As the image contains 2 root file systems, it has a size of 7 Gigabytes.

It also will create a binary for updating the system at
`build/tmp/deploy/images/iot2050/iot2050-image-swu-example-iot2050-debian-iot2050.swu`

### Update an image with SWUpdate

The following steps are necessary to update an image created with SWUpdate
support.

1. Transfer the SWUpdate binary
`iot2050-image-swu-example-iot2050-debian-iot2050.swu` to the target system.

2. Update the system with SWUpdate by executing:

```shell
$ swupdate -i iot2050-image-swu-example-iot2050-debian-iot2050.swu
```

You can find more details and options for the command `swupdate` in the
[SWUpdate
documentation](https://sbabic.github.io/swupdate/swupdate.html#running-swupdate).

NOTE: The used SWUpdate package does not contain a web-app example.

SWUpdate will write the image to the unused root partition and updates the EFI
Boot Guard state. EFI Boot Guard is the bootloader that controls which of the
two kernels and root file systems are booted.

3. Reboot the system into the new root file system. The switch between the root
file systems occurs automatically and requires no user interaction.

4. Confirm that the new root file system is correctly booted.

After a reboot, the device boots into the new root file system. If the boot is
successful the update process needs to be completed by calling:

```shell
$ complete_update.sh
```

The script sets the update state in the EFI Boot Guard configuration to the
initial state.

If the update is deemed failed, resetting the device will select the previous
root file system.

### U-Boot environment

The bootloader environment needs to be adapted to select the correct root file
system during boot. This adaptation occurs automatically during the first boot
by executing the `patch-u-boot-env.service`. This systemd-service activates the
hardware watchdog in the U-Boot environment, setting it to 60 seconds by
default.

#### Revert to the default environment

If it is necessary to revert to the default U-Boot environment the following
command can be used:
```shell
$ fw_setenv -f /etc/u-boot-initial-env
```
