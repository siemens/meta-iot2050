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

DESCRIPTION = "IOT2050 login security baseline"

DEBIAN_DEPENDS = "cracklib-runtime, libpam-runtime, libpam-modules, libpam-pwquality, openssh-server, passwd, python3, systemd, wamerican"

GROUPS += "iot2050-admin"

IOT2050_FAILLOCK_DENY ?= "5"
IOT2050_FAILLOCK_FAIL_INTERVAL ?= "900"
IOT2050_FAILLOCK_UNLOCK_TIME ?= "900"
IOT2050_FAILLOCK_EVEN_DENY_ROOT ?= "1"
IOT2050_FAILLOCK_ROOT_UNLOCK_TIME ?= "900"
IOT2050_LOCK_ROOT_PASSWORD ?= "1"

SRC_URI = " \
    file://iot2050-account-admin \
    file://iot2050-failed-login \
    file://iot2050-login-admin \
    file://iot2050-login-backend \
    file://iot2050-login-backend.service \
    file://iot2050-login-backend.socket \
    file://login-backend-client.py \
    file://login-backend-service.py \
    file://postinst.tmpl \
"

TEMPLATE_FILES = "postinst.tmpl"
TEMPLATE_VARS = "IOT2050_FAILLOCK_DENY IOT2050_FAILLOCK_FAIL_INTERVAL IOT2050_FAILLOCK_UNLOCK_TIME IOT2050_FAILLOCK_EVEN_DENY_ROOT IOT2050_FAILLOCK_ROOT_UNLOCK_TIME IOT2050_LOCK_ROOT_PASSWORD"

do_install() {
    install -d -m 755 ${D}/etc/systemd/system
    install -m 644 ${WORKDIR}/iot2050-login-backend.service ${D}/etc/systemd/system/
    install -m 644 ${WORKDIR}/iot2050-login-backend.socket ${D}/etc/systemd/system/

    install -d -m 755 ${D}/usr/lib/iot2050
    install -m 755 ${WORKDIR}/login-backend-client.py ${D}/usr/lib/iot2050/
    install -m 755 ${WORKDIR}/login-backend-service.py ${D}/usr/lib/iot2050/

    install -d -m 755 ${D}/usr/sbin
    install -m 755 ${WORKDIR}/iot2050-account-admin ${D}/usr/sbin/
    install -m 755 ${WORKDIR}/iot2050-failed-login ${D}/usr/sbin/
    install -m 755 ${WORKDIR}/iot2050-login-admin ${D}/usr/sbin/
    install -m 755 ${WORKDIR}/iot2050-login-backend ${D}/usr/sbin/
}
