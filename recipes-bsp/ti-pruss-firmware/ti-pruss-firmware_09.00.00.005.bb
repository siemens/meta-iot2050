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
    ${@get_prueth_fw(d, 'am65x-sr2-pru0-prueth-fw.elf', '87b565bf95f778b52fb67c50282e6b635b8234b880708991ed53c3c09d8b4d80')} \
    ${@get_prueth_fw(d, 'am65x-sr2-pru1-prueth-fw.elf', '82851d7d1ed19a9418e345ceffd52903899384e2b5ae8ca9c588ed6148726853')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu0-prueth-fw.elf', '7e7e1e3f1815f9231187ff54bbe6bf519c1379f36969a1759a0f6a139b16b085')} \
    ${@get_prueth_fw(d, 'am65x-sr2-rtu1-prueth-fw.elf', '12d30b26b34cf15b215d57546da5e2d53682506043ea20e2b37022a5040258a3')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru0-prueth-fw.elf', 'ea17ea678f91c3a3e4382377a84f42d2f1f64b0525014b74f40836d4947cc815')} \
    ${@get_prueth_fw(d, 'am65x-sr2-txpru1-prueth-fw.elf', '7d1bcde936bdf9606c1810c3316439e79d6d8b6f2751919d1d654abeb1545613')} \
    "

DEB_BUILD_OPTIONS = "nostrip"

do_install() {
    install -v -d ${D}/lib/firmware/ti-pruss
    install -v -m 644 ${WORKDIR}/am65x-*.elf ${D}/lib/firmware/ti-pruss
}
