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
    ${@get_prueth_fw(d, 'am65x-sr2-pru0-prueth-fw.elf', '21526f5c2a6a78f31e0e060867e41793b2470457ec0ebcff0ce38e3dba8a3d7f')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru1-prueth-fw.elf', 'b19df885af9b2b5724a4380e1498ad83911bcf238a1b9968e9be3c33c1956f15')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu0-prueth-fw.elf', '74aa86d4c9e9e699f683fac0bdea5a78dee3a3dbd4ce0b903ed91055f043e059')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu1-prueth-fw.elf', '179495fe4f77782d74f99f67ab9aaed6eb66405c9b87f47f346cdb5f03f95d26')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru0-prueth-fw.elf', 'd6c2eee72555c86fa4fe6e20fafd54dcee5403196856aed6750374e8c9a0d2c3')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru1-prueth-fw.elf', '8923ec1b1e82dd794440957c5149f370e239c8b782666aba7911fdc76c419d95')} \
    "

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/am65x-*.elf ${D}/lib/firmware/ti-pruss
}
