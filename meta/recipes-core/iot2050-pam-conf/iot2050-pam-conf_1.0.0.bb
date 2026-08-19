#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 PAM configuration"

DEBIAN_DEPENDS = "cracklib-runtime, libpam-runtime, libpam-modules, libpam-pwquality, passwd, python3, systemd, wamerican"

SRC_URI = " \
    file://pam-configs/iot2050-failed-login-lockout \
    file://pam-configs/iot2050-failed-login-preauth \
    file://pam-configs/iot2050-failed-login-success \
    file://pam-configs/iot2050-password-quality \
    file://postinst \
"

do_install() {
    install -d -m 755 ${D}/usr/share/pam-configs
    install -m 644 ${WORKDIR}/pam-configs/iot2050-failed-login-lockout ${D}/usr/share/pam-configs/
    install -m 644 ${WORKDIR}/pam-configs/iot2050-failed-login-preauth ${D}/usr/share/pam-configs/
    install -m 644 ${WORKDIR}/pam-configs/iot2050-failed-login-success ${D}/usr/share/pam-configs/
    install -m 644 ${WORKDIR}/pam-configs/iot2050-password-quality ${D}/usr/share/pam-configs/
}