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

PR = "2"

inherit dpkg-raw

DESCRIPTION = "IOT2050 Extended IO Manager"
MAINTAINER = "baocheng.su@siemens.com"

SRC_URI = " \
    file://iot2050-eiofsd.service \
    "

SRC_URI_BIN_PREDOWNLOAD = " \
    file://bin/iot2050-eiofsd \
    file://bin/map3-fw.bin \
    file://bin/firmware-version \
    "

DEBIAN_DEPENDS = "libfuse2, libgpiod3"

python () {
    import os
    import textwrap

    src_uri_bin_str = d.getVar('SRC_URI_BIN_PREDOWNLOAD') or ""
    if not src_uri_bin_str:
        return

    uris_to_keep = []
    missing_bins = []

    for uri in src_uri_bin_str.split():
        try:
            bin_name = os.path.basename(uri)
            fetcher = bb.fetch2.Fetch([uri], d)
            bin_path = fetcher.localpath(uri)

            if os.path.exists(bin_path):
                uris_to_keep.append(uri)
            else:
                missing_bins.append(bin_name)

        except bb.fetch2.FetchError:
            missing_bins.append(bin_name)

    if missing_bins:
        warning_message = textwrap.dedent(f"""
            *******************************************************************
            WARNING: The following EIO binary files were not found:
            {', '.join(missing_bins)}

            The build will continue without EIO support. Please download the correct
            binaries from SIOS for a full build.
            See meta-sm/recipes-app/iot2050-eiofsd/files/bin/README.md for details.
            *******************************************************************
            """)
        bb.warn(warning_message)

    d.setVar('SRC_URI', d.getVar('SRC_URI') + ' ' + ' '.join(uris_to_keep))
}

do_install() {
    install -v -d ${D}/usr/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eiofsd.service ${D}/usr/lib/systemd/system/

    # Only install the binaries if they were fetched and exist in the WORKDIR
    if [ -f "${WORKDIR}/bin/iot2050-eiofsd" ]; then
        install -v -d ${D}/usr/bin/
        install -v -m 755 ${WORKDIR}/bin/iot2050-eiofsd ${D}/usr/bin/
    fi

    if [ -f "${WORKDIR}/bin/map3-fw.bin" ] && [ -f "${WORKDIR}/bin/firmware-version" ]; then
        install -v -d ${D}/usr/lib/iot2050/eio/
        install -v -m 755 ${WORKDIR}/bin/map3-fw.bin ${D}/usr/lib/iot2050/eio/
        install -v -m 755 ${WORKDIR}/bin/firmware-version ${D}/usr/lib/iot2050/eio/
    fi

    install -v -d ${D}/eiofs
}
