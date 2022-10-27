# Building and programming the boot loader

## Building the image

The boot loader for PG1 and PG2 boards is built like this:

```shell
./kas-container build kas-iot2050-boot-pg1.yml
./kas-container build kas-iot2050-boot-pg2.yml
```

After the build the boot images are under

```text
build/tmp/deploy/images/iot2050/iot2050-pg1-image-boot.bin
build/tmp/deploy/images/iot2050/iot2050-pg2-image-boot.bin
```

## Flashing the image

> :warning:
> Flashing an incorrect image may brick the device!

Write `iot2050-pgN-image-boot.bin` to an SD card and insert that into
the target device. Then boot into the U-Boot shell and execute there:

```shell
sf probe
load mmc 0:1 $loadaddr /path/to/iot2050-pgN-image-boot.bin
sf update $loadaddr 0x0 $filesize
```

## Recovering a bricked device

If the device does not come up anymore after flashing the boot loader, you can
recover it with the help of an external flash programmer. Known to work are the
Dediprog SF100 or SF600. Attach the programmer to X17, then run the following
on the host machine:

```shell
dpcmd --vcc 2 -v -u iot2050-pgN-image-boot.bin
```

Also, as alternative it is possible to use flash programmer which can work
with Winbond chips (W25Q128), as example - ch341a. The flash chip is located on
the back side of the board.

> :warning:
> This way is not preferred, please, use Dediprog flash programmers if possible.

![overview](back_iot2050.png)


Install flashrom with:

```shell
apt-get install flashrom
```

Attach the grabber to the flash chip, then run the following on the host machine:

If the the size of the uboot file doesn't match the flash chip's size (16M)
execute this command:

```shell
truncate -s 16M iot2050-image-boot.bin
```

Then upgrade the firmware:

```shell
flashrom -p ch341a_spi -c W25Q128.V -w iot2050-image-boot.bin
```

## eMMC RPMB key provisioning

To utilize the eMMC RPMB as the backend for secure storage, an otp key is
required to be programmed into the eMMC RPMB. This key is unique per-device.

A special firmware build is required to run in a secure operating environment to
program this key into RPMB. To build this special firmware:

```shell
./kas-container build kas-iot2050-boot-pg2.yml:kas/opt/rpmb-setup.yml
```

This will build a special OPTee binary for generating and programming the otp
key, together with a special U-Boot binary for kicking off the key programming.

> :warning:
> This special firmware must NOT be signed.
>
> This special firmware must run in a secure operating environment.
>
> To protected the programmed RPMB key, it is required to flash a signed image,
> program secure boot keys and enable secure boot.


To kick off the key programming, when booting the special firmware, press any
key to enter to the u-boot console and issue below commands:

```
mmc dev 1
optee_rpmb write_pvalue paired 1
optee_rpmb read_pvalue paired 2
```

`mmc dev 1` is for setting the eMMC as the current mmc device.

`optee_rpmb write_pvalue paired 1` triggers the RPMB key programming, then write
a persistent value 1 named with `paired` to the RPMB based secure storage. A
successful running of this command returns:
```
Wrote 2 bytes
```

`optee_rpmb read_pvalue paired 2` reads back the written persistent value for
checking. It should return
```
Read 2 bytes, value = 1
```
