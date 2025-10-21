##
# Copyright (c) Siemens AG, 2025
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
##

SUMMARY = "IoT2050 base feature aggregation meta package"

IOT2050_META_PACKAGES ?= " \
    ${@ 'u-boot-${MACHINE}-config' if d.getVar('QEMU_IMAGE') != '1' else '' } \
    iot2050-firmware \
    iot2050-base-packages \
    libubootenv-tool \
    "
