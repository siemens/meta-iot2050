# Building and programming the boot loader

## Building the image

The boot loader for the basic version is built like this:

```shell
./kas-docker --isar build kas-iot2050-boot-basic.yml
```

The advanced version is built like this:

```shell
./kas-docker --isar build kas-iot2050-boot-advanced.yml
```

After the build the boot image is under

```text
build/tmp/deploy/images/iot2050/iot2050-image-boot-basic.bin
```

or

```text
build/tmp/deploy/images/iot2050/iot2050-image-boot-advanced.bin
```

## Flashing the image

> :warning:
> Flashing an incorrect image may brick the device!

Write `iot2050-image-boot-<variant>.bin` to an SD card and insert that into
the target device. Then boot into the U-Boot shell and execute there:

```shell
sf probe
load mmc 0:1 $loadaddr /path/to/iot2050-image-boot-<variant>.bin
sf update $loadaddr 0x0 $filesize
```

> :note:
> When updating the boot loader of the BASIC variant, make sure to remove
> 0022-iot2050-Roll-back-basic-dtb-to-V01.00.00.1-release.patch from the kernel
> patch queue in recipes-kernel/linux/linux-iot2050_*.bb.

## Recovering a bricked device

If the device does not come up anymore after flashing the boot loader, you can
recover it with the help of an external flash programmer. Known to work are the
Dediprog SF100 or SF600. Attach the programmer to X17, then run the following
on the host machine:

```shell
dpcmd --vcc 2 -v -u iot2050-image-boot-<variant>.bin
```
