#
# Copyright (c) Siemens AG, 2021-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

SRC_URI = " \
    file://am65x-sr2-pru0-prueth-fw.elf \
    file://am65x-sr2-pru1-prueth-fw.elf \
    file://am65x-sr2-rtu0-prueth-fw.elf \
    file://am65x-sr2-rtu1-prueth-fw.elf \
    file://am65x-sr2-txpru0-prueth-fw.elf \
    file://am65x-sr2-txpru1-prueth-fw.elf \
    "

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/am65x-*.elf ${D}/lib/firmware/ti-pruss
}
