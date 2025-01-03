# SPDX-FileCopyrightText: Copyright 2023-2024 Siemens AG
# SPDX-License-Identifier: MIT
DESCRIPTION = "hailo firmware - hailo8 chip firmware (hailo_fw.bin)"

BASE_URI = "https://hailo-hailort.s3.eu-west-2.amazonaws.com"
FW_AWS_DIR = "Hailo8/${PV}/FW"
FW = "hailo8_fw.${PV}.bin"
LICENSE_FILE = "LICENSE"

SRC_URI = "${BASE_URI}/${FW_AWS_DIR}/${FW};name=firmware \
	   ${BASE_URI}/${FW_AWS_DIR}/${LICENSE_FILE};name=license"
SRC_URI[firmware.sha256sum] = "bfa576dd782359d74cabcb19e87c3a934dce03dea0785e41f86fecc9a687a92b"
SRC_URI[license.md5sum]  = "263ee034adc02556d59ab1ebdaea2cda"

LICENSE = "LICENSE"
LIC_FILES_CHKSUM = "file://${WORKDIR}/${LICENSE_FILE};md5=263ee034adc02556d59ab1ebdaea2cda"

FW_PATH = "${WORKDIR}/${FW}"

DPKG_ARCH = "all"

inherit dpkg-raw

do_install() {
	# Stores hailo8_fw.bin in the rootfs under /lib/firmware/hailo/
	install -d ${D}/lib/firmware/hailo
	install -m 0644 ${FW_PATH} ${D}/lib/firmware/hailo/hailo8_fw.bin
}
