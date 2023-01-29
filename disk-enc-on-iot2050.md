# Disk enc POC on IOT2050

## env set up

- This branch head
- IOT2050 PG2 or M2
- RPMB key paired via u-boot command line, follow recipes-bsp/u-boot/README.md#L75

## dm-crypt table

```
<start_sector> <size> <target name> <cipher> <key> <iv_offset> <device path> <offset> [<#opt_params> <opt_params>]
    <start_sector>0</start_sector>
    <size>31080448</size> # size of emmc: $(blockdev --getsz /dev/mmcblk1)
    <target name>crypt</target>
    <cipher>capi:xts(aes)-plain64</cipher>
    <key>:32:encrypted:enckey</key>
    <iv_offset>0</iv_offset>
    <device path>/dev/mmcblk1</device path>
    <offset>0</offset>
```

## 1st time setup

```bash

cd ~

### create the trusted key and the encrypted key
keyctl pipe $(keyctl add trusted kmk "new 32" @u) > kmk.blob
keyctl pipe $(keyctl add encrypted enckey "new trusted:kmk 32" @u) > enckey.blob

### create the dm-crypt target at /dev/mapper/x
dmsetup create x --table "0 31080448 crypt capi:xts(aes)-plain64 :32:encrypted:enckey 0 /dev/mmcblk1 0"
partprobe

### partition the mapper device and create the filesystem
fdisk /dev/mapper/x
partprobe
mkfs.ext4 /dev/mapper/x1

### mount the device and write a test file
mkdir test 
mount /dev/mapper/x1 test
dd if=/dev/zero of=test/test.bin bs=100M count=10 status=progress oflag=direct
```

## Later reboot

```bash
cd ~

### reconstrut the keys
keyctl add trusted kmk "load `cat kmk.blob`" @u
keyctl add encrypted enckey "load `cat enckey.blob`" @u

### create the dm-crypt target at /dev/mapper/x
dmsetup create x --table "0 31080448 crypt capi:xts(aes)-plain64 :32:encrypted:enckey 0 /dev/mmcblk1 0"
partprobe

### mount the device and dump the test file
mount /dev/mapper/x1 test
hexdump test/test.bin
```
