#
# Copyright (c) Siemens AG, 2023-2025
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 Extended IO Manager"
MAINTAINER = "baocheng.su@siemens.com"

SRC_URI = " \
    file://iot2050-eiofsd.service \
    "

SRC_URI_BIN_PREDOWNLOAD = "${@ ' \
    file://bin/iot2050-eiofsd \
    file://bin/map3-fw.bin \
    file://bin/firmware-version ' if d.getVar('IOT2050_EIO_SUPPORT') == '1' else '' } \
    "

SRC_URI += "${SRC_URI_BIN_PREDOWNLOAD}"

DEBIAN_DEPENDS = "libfuse2, libgpiod3"

python do_fetch:prepend() {
    import textwrap
    src_uri_bin = (d.getVar('SRC_URI_BIN_PREDOWNLOAD') or "").split()
    if len(src_uri_bin) == 0:
        return

    try:
        fetcher = bb.fetch2.Fetch(src_uri_bin, d)
        fetcher.checkstatus()
    except bb.fetch2.BBFetchException as e:
        text = textwrap.dedent(f"""\
            {str(e)}
            Please download the EIO binaries from SIOS before building!
            Check the README.md for details.""")
        bb.fatal(text)
}

do_install() {
    install -v -d ${D}/usr/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eiofsd.service ${D}/usr/lib/systemd/system/

    install -v -d ${D}/usr/bin/
    install -v -m 755 ${WORKDIR}/bin/iot2050-eiofsd ${D}/usr/bin/

    install -v -d ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/bin/map3-fw.bin ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/bin/firmware-version ${D}/usr/lib/iot2050/eio/
    install -v -d ${D}/eiofs
}
