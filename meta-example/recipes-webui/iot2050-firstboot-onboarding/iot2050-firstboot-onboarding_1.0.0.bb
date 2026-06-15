#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 first-boot onboarding web service"

DEBIAN_DEPENDS = "cockpit, iot2050-web-gateway-nginx, nodejs, passwd, python3, sudo, systemd"

SRC_URI = " \
    file://iot2050-firstboot-onboarding.service \
    file://iot2050-firstboot-onboarding.js \
    file://iot2050-firstboot-onboarding-launcher \
    file://iot2050-firstboot-apply-user.py \
    file://iot2050-firstboot-finalize.sh \
    file://postinst \
    file://www/index.html \
    file://www/app.css \
    file://www/app.js \
    file://www/favicon.ico \
    file://www/locale.js \
    file://i18n/catalog.json \
    file://i18n/generate-po-bundles.py \
    "

do_install() {
    build_year="$(date +%Y)"

    install -d -m 755 ${D}/usr/lib/systemd/system
    install -m 644 ${WORKDIR}/iot2050-firstboot-onboarding.service ${D}/usr/lib/systemd/system/

    install -d -m 755 ${D}/usr/lib/iot2050/onboarding
    install -m 755 ${WORKDIR}/iot2050-firstboot-onboarding.js ${D}/usr/lib/iot2050/onboarding/
    install -m 755 ${WORKDIR}/iot2050-firstboot-apply-user.py ${D}/usr/lib/iot2050/onboarding/
    install -m 755 ${WORKDIR}/iot2050-firstboot-finalize.sh ${D}/usr/lib/iot2050/onboarding/

    install -d -m 755 ${D}/usr/share/iot2050-firstboot-onboarding
    sed "s/@BUILD_YEAR@/${build_year}/g" ${WORKDIR}/www/index.html > ${D}/usr/share/iot2050-firstboot-onboarding/index.html
    chmod 0644 ${D}/usr/share/iot2050-firstboot-onboarding/index.html
    install -m 644 ${WORKDIR}/www/app.css ${D}/usr/share/iot2050-firstboot-onboarding/
    install -m 644 ${WORKDIR}/www/app.js ${D}/usr/share/iot2050-firstboot-onboarding/
    install -m 644 ${WORKDIR}/www/locale.js ${D}/usr/share/iot2050-firstboot-onboarding/
    install -m 644 ${WORKDIR}/www/favicon.ico ${D}/usr/share/iot2050-firstboot-onboarding/favicon.ico
    PYTHONDONTWRITEBYTECODE=1 python3 -B ${WORKDIR}/i18n/generate-po-bundles.py \
        --source ${WORKDIR}/i18n/catalog.json \
        --output-dir ${D}/usr/share/iot2050-firstboot-onboarding

    install -d -m 755 ${D}/usr/bin
    install -m 755 ${WORKDIR}/iot2050-firstboot-onboarding-launcher ${D}/usr/bin/iot2050-firstboot-onboarding
}
