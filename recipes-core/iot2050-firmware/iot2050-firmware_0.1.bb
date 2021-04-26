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

DEBIAN_DEPENDS = "u-boot-tools"

SRC_URI = " \
    file://postinst \
    file://ti-pruss/am65x-pru0-prueth-fw.elf \
    file://ti-pruss/am65x-pru1-prueth-fw.elf \
    file://ti-pruss/am65x-rtu0-prueth-fw.elf \
    file://ti-pruss/am65x-rtu1-prueth-fw.elf \
    file://rti_dwwdtest/iot2050/csl_rti_dwwd_test_app_mcu1_0_release.xer5f \
    file://fw_env.config"


do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/ti-pruss/* ${D}/lib/firmware/ti-pruss

    install -v -d ${D}/lib/firmware/rti_dwwdtest/iot2050
    install -v -m 644 ${WORKDIR}/rti_dwwdtest/iot2050/* ${D}/lib/firmware/rti_dwwdtest/iot2050

    install -v -d ${D}/etc
    install -v -m 644 ${WORKDIR}/fw_env.config ${D}/etc/
}
