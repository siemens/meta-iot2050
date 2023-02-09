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
    ${@get_prueth_fw(d, 'am65x-sr2-pru0-prueth-fw.elf', '926229ff1d7e8bb4213921710abe3c6d04e9077d79ca870b713d433ea93f3785')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru1-prueth-fw.elf', '351132c01b1d160154e4c7a69b97d3c4625b2b1f2a46218d6756ecb5d8d98564')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu0-prueth-fw.elf', 'ca136741887640cff0bd3c222f80e28e745d2a5c88114cad21751e5892850c6f')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu1-prueth-fw.elf', 'ae13bc7e956ece1fab6f8a65eda2a611e7867f5417325b4aa431cbc8b9392945')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru0-prueth-fw.elf', 'c3fb9b0f37393837ff23488878b3dffd4570ffd381142c33f72bc3abef3b82d4')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru1-prueth-fw.elf', '771047d85815c918f46a3cd5c3cd77c3df95c6287640d1bb0c818f5e73855f2c')} \
    "

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/am65x-*.elf ${D}/lib/firmware/ti-pruss
}
