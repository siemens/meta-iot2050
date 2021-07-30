#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DEBIAN_DEPENDS = "u-boot-tools, k3-rti-wdt"
DEPENDS = "k3-rti-wdt"

SRC_URI = " \
    file://ti-pruss/am65x-pru0-prueth-fw.elf \
    file://ti-pruss/am65x-pru1-prueth-fw.elf \
    file://ti-pruss/am65x-rtu0-prueth-fw.elf \
    file://ti-pruss/am65x-rtu1-prueth-fw.elf \
    file://fw_env.config"

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/ti-pruss/* ${D}/lib/firmware/ti-pruss

    install -v -d ${D}/etc
    install -v -m 644 ${WORKDIR}/fw_env.config ${D}/etc/
}

do_prepare_build_append() {
    echo "/lib/firmware/k3-rti-wdt.fw /lib/firmware/am65x-mcu-r5f0_0-fw" > ${S}/debian/links
}
