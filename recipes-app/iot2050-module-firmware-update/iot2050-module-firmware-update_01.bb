#
# Copyright (c) Siemens AG, 2024
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

DESCRIPTION = "IOT2050 Customized External Signal Module Firmware Update"
MAINTAINER = "huaqian.li@siemens.com"

SRC_URI = " \
    file://iot2050-module-firmware-update.tmpl"

TEMPLATE_FILES = "iot2050-module-firmware-update.tmpl"

inherit dpkg-raw

do_install() {
    install -v -d ${D}/usr/sbin/
    install -v -m 755 ${WORKDIR}/iot2050-module-firmware-update ${D}/usr/sbin/
}

do_deploy_deb[dirs] = "${DEPLOY_DIR_IMAGE}"
