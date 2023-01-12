#
# Copyright (c) Siemens AG, 2021
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
    ${@get_prueth_fw(d, 'am65x-sr2-pru0-prueth-fw.elf', '8b709dbe96b5ae793e4865f24708c973ea2343df1c20e2199ba139868821eb93')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru1-prueth-fw.elf', 'aacc9f2359fbd0dcb251cd8fd48275257a95075b640872192099552fafef4678')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu0-prueth-fw.elf', 'fb154656f7cf2dd398a35968dfeaedda1fd57e916ee82b8d6fe58ad4d018e53b')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu1-prueth-fw.elf', 'fc29c8f5e34234e96dcdda3a2f8628dec61c2c150e5e2896075b13a2d859acd6')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru0-prueth-fw.elf', '96e1dd06feb3f05915dc61fb1b11b27674484749f9881ef02ebb48ac07f1386e')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru1-prueth-fw.elf', '389ff8bdee84d66f0b1a8e02c2b8517b0b61a263fb65c18761e40eb83e09e9d2')} \
    "

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/am65x-*.elf ${D}/lib/firmware/ti-pruss
}
