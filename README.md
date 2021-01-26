# META-IOT2050

This [Isar](https://github.com/ilbers/isar) layer contains recipes,
configuration and other artifacts that are specific to  Debian-based
IOT2050 product.

## Build example image

Before building the system, you will need to install docker on build host.
For example under Debian Linux

```shell
sudo apt install docker.io
```

Then build the example image

```shell
./kas-container build kas-iot2050-example.yml
```

Build the example RT image, for example

```shell
./kas-container build kas-iot2050-example.yml:kas/opt/preempt-rt.yml
```

Using 3rd-party mirrors, for example

```shell
./kas-container build kas-iot2050-example.yml:kas/opt/mirror-example.yml
```

After build complete, the final image is under

```text
build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic.img
```

## Build user SDK
>>>
**Note:** Current SDK only supports Linux x86-64 host machine
>>>

```shell
./kas-container build kas-iot2050-example.yml:kas/opt/sdk.yml
```

After build complete, the SDK tarball is located at

```text
build/tmp/deploy/images/iot2050/sdk-isar-arm64.tar.xz
```

Please follow the further instruction file `README.sdk` under the SDK tarball

## Clean build result

```shell
./kas-container --isar clean
```

## Build released version

First checkout the desired tag. Then build the image or sdk by appending the `kas/opt/package-lock.yml`:

```shell
# example image
./kas-container build kas-iot2050-example.yml:kas/opt/package-lock.yml

# example rt image
./kas-container build kas-iot2050-example.yml:kas/opt/preempt-rt.yml:kas/opt/package-lock.yml

# bootloader for advanced board
./kas-container build kas-iot2050-boot-advanced.yml:kas/opt/package-lock.yml

# bootloader for basic board
./kas-container build kas-iot2050-boot-basic.yml:kas/opt/package-lock.yml

# SDK
./kas-container build kas-iot2050-example.yml:kas/opt/sdk.yml:kas/opt/package-lock.yml
```

## Booting the Image from SD card

Under Linux, insert an unused SD card. Assuming the SD card takes device
/dev/mmcblk0, use dd to copy the image to it. For example:

```shell
$ sudo dd if=build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic.img \
          of=/dev/mmcblk0 bs=4M oflag=sync
```

Alternatively, install the bmap-tools package and run the following command which is generally faster and safer:

```shell
$ sudo bmaptool copy build/tmp/deploy/images/iot2050/iot2050-image-example-iot2050-debian-iot2050.wic.img /dev/mmcblk0
```

The example image starts with the IP 192.168.200.1 preconfigured on the first
Ethernet interface, and use DHCP at another. You can use ssh to connect to the system.

The BSP image does not configure the network. If you want to ssh into the
system, you can use the root terminal via UART to ifconfig the IP address and
use that to ssh in.

NOTE: To login, the default username and password is `root`.
And you are required to change the default password when first login.

## Selecting a boot device

By default, the boot loader will pick the first bootable device. If that device
may no longer fully start, you can select an alternative boot device in the
U-Boot shell. Attach a USB-UART adapter to X14, connect it to a host PC and
open a terminal program on that port. Reset the device and interrupt the boot
when it counts down ("Hit any key to stop autoboot"). Then type

```shell
=> setenv boot_targets mmc0
=> run distro_bootcmd
```

to boot from the microSD card. Use `usb0` for the first USB mass storage
device.

NOTE: This selection is not persistent. The boot loader will fall back to its
default boot order after reset.
