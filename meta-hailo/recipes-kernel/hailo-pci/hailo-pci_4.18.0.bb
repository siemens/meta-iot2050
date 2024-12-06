# SPDX-FileCopyrightText: Copyright 2023-2024 Siemens AG
# SPDX-License-Identifier: MIT
DESCRIPTION = "hailo pcie driver - the kernel driver for pci communication with hailo8"

LICENSE = "gpl-2.0"
LIC_FILES_CHKSUM = "file://${LAYERDIR_core}/licenses/COPYING.GPLv2;md5=751419260aa954499f7abaabaa882bbe"

SRC_URI = "git://git@github.com/hailo-ai/hailort-drivers.git;protocol=https;branch=master"
SRCREV = "7161f9ee5918029bd4497f590003c2f87ec32507"

require recipes-kernel/linux-module/module.inc

S = "${WORKDIR}/git"
MODULE_DIR = "$(PWD)/linux/pcie"

do_prepare_build:append() {
    cp ${S}/linux/pcie/51-hailo-udev.rules ${S}/debian/${BPN}.udev
}
