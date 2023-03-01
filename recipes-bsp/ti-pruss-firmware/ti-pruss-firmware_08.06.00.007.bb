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

def get_prueth_fw(d, file, sha=''):
    uri = "https://git.ti.com/cgit/processor-firmware/ti-linux-firmware/plain/ti-pruss/{file}?h={pv};downloadfilename={file}".format(
        file=file, pv=d.getVar('PV'), sha=sha)
    if len(sha) > 0:
        uri += ';sha256sum=' + sha
    return uri

SRC_URI = " \
    ${@get_prueth_fw(d, 'am65x-pru0-prueth-fw.elf', '45b83aa8408ece0864d816cad00164da4778967ae3120eb153b986647ffd605d')} \
    ${@get_prueth_fw(d, 'am65x-pru1-prueth-fw.elf', '56cb71d205810a3609a5dff950fa7d7ea6b383d9d2fb6b1f2116ba58527f2f7f')} \
    ${@get_prueth_fw(d, 'am65x-rtu0-prueth-fw.elf', 'f01f58cdfad61652205c7ea6ed41ef0a759f63f02551447d940f919be691543f')} \
    ${@get_prueth_fw(d, 'am65x-rtu1-prueth-fw.elf', '3b905819ef3a7c4daa560106f3bba62cace55380c5ce40a22f7de232c0083052')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru0-prueth-fw.elf', '70405580d45065f7046bdf9eb14e9ea4973d508587ce52834dba228f65413ce2')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru1-prueth-fw.elf', '2e8b0d4a2e7b6f82d50d3cb2f0133bec19e6b1487af7304b67ea1ed9950a7d13')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu0-prueth-fw.elf', '8d95e5eefa2c950eb56e320318fa6b9fffb69cb9fb056ec5a6ccb8c0ca5cddb0')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu1-prueth-fw.elf', 'd7d12ad17dfde286e9f6607719b44f0d9b9b69eb06d4fabaae37a5aa6840fdcb')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru0-prueth-fw.elf', 'a92a105998230ab282588f1dac33a6c221a6f33dd4ff2a52d16a169b2a0a5703')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru1-prueth-fw.elf', '85215d76a45837c3ba5323da496305b7ff92c475d963e631765ad0afe01629be')} \
    "

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/am65x-*.elf ${D}/lib/firmware/ti-pruss
}
