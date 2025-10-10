#
# Copyright (c) Siemens AG, 2021-2023
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
PR = "1"
inherit dpkg-raw

def get_prueth_fw(d, file, sha=''):
    uri = "https://github.com/TexasInstruments/ti-linux-firmware/raw/refs/tags/{pv}/ti-pruss/{file};downloadfilename={file}".format(
        file=file, pv=d.getVar('PV'), sha=sha)
    if len(sha) > 0:
        uri += ';sha256sum=' + sha
    return uri

SRC_URI = " \
    ${@get_prueth_fw(d, 'am65x-pru0-prueth-fw.elf', '45b83aa8408ece0864d816cad00164da4778967ae3120eb153b986647ffd605d')} \
    ${@get_prueth_fw(d, 'am65x-pru1-prueth-fw.elf', '56cb71d205810a3609a5dff950fa7d7ea6b383d9d2fb6b1f2116ba58527f2f7f')} \
    ${@get_prueth_fw(d, 'am65x-rtu0-prueth-fw.elf', 'f01f58cdfad61652205c7ea6ed41ef0a759f63f02551447d940f919be691543f')} \
    ${@get_prueth_fw(d, 'am65x-rtu1-prueth-fw.elf', '3b905819ef3a7c4daa560106f3bba62cace55380c5ce40a22f7de232c0083052')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru0-prueth-fw.elf', '6acb4e83ac95a97caa768782042314b58bc8783b63c38b05bc7560e57aecb9a1')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru1-prueth-fw.elf', 'b694e18de8d58b5b7de2047f263b1c8ba93e794027bc7088473c867019685f01')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu0-prueth-fw.elf', '96571d193084251765340256d8d7633c7e08754a70ddfc8231407d3bd1c3af9b')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu1-prueth-fw.elf', 'bd5af0232993228ec1e6f17680bbaec9087899c580df9ad14bd59e16be757467')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru0-prueth-fw.elf', '7d757a50f2907f663261e66cd3df3aa1e302f9c0568654d5a2aa91696ac1d1a6')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru1-prueth-fw.elf', '17e08a3005e23cb92fd6333a108929533720c40d45e021ad1d6a69b768e6dbfc')} \
    "

DEB_BUILD_OPTIONS = "nostrip"

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/am65x-*.elf ${D}/lib/firmware/ti-pruss
}
