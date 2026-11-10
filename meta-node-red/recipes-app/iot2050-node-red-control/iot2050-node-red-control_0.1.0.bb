# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT
inherit dpkg-raw
DESCRIPTION = "Cockpit-facing Node-RED activation and isolated HTTPS gateway"
DEBIAN_DEPENDS = "iot2050-node-red-auth, node-red, nginx, python3-dbus, python3-gi, polkitd, openssl, systemd"
DEPENDS = "iot2050-node-red-auth node-red"

SRC_URI = "file://control.py file://dbus-service.py file://gate file://nginx.conf file://nginx-runtime.conf \
    file://node-red.conf file://com.siemens.iot2050.NodeRed.conf \
    file://com.siemens.iot2050.NodeRed.service file://com.siemens.iot2050.node-red.policy \
    file://iot2050-node-red-control.service file://sysusers.conf file://tmpfiles.conf file://postinst"

do_install() {
    install -d ${D}/usr/lib/iot2050/node-red-control
    install -m 644 ${WORKDIR}/control.py ${WORKDIR}/dbus-service.py ${D}/usr/lib/iot2050/node-red-control/
    install -m 755 ${WORKDIR}/gate ${D}/usr/lib/iot2050/node-red-control/
    install -d ${D}/usr/share/iot2050/node-red-control
    install -m 644 ${WORKDIR}/nginx.conf ${D}/usr/share/iot2050/node-red-control/
    install -d ${D}/etc/nginx/conf.d
    install -m 644 ${WORKDIR}/nginx-runtime.conf ${D}/etc/nginx/conf.d/iot2050-node-red-runtime.conf
    install -d ${D}/usr/lib/systemd/system/node-red.service.d
    install -m 644 ${WORKDIR}/node-red.conf ${D}/usr/lib/systemd/system/node-red.service.d/iot2050-hardening.conf
    install -m 644 ${WORKDIR}/iot2050-node-red-control.service ${D}/usr/lib/systemd/system/
    install -d ${D}/usr/share/dbus-1/system.d ${D}/usr/share/dbus-1/system-services ${D}/usr/share/polkit-1/actions
    install -m 644 ${WORKDIR}/com.siemens.iot2050.NodeRed.conf ${D}/usr/share/dbus-1/system.d/
    install -m 644 ${WORKDIR}/com.siemens.iot2050.NodeRed.service ${D}/usr/share/dbus-1/system-services/
    install -m 644 ${WORKDIR}/com.siemens.iot2050.node-red.policy ${D}/usr/share/polkit-1/actions/
    install -d ${D}/usr/lib/sysusers.d ${D}/usr/lib/tmpfiles.d
    install -m 644 ${WORKDIR}/sysusers.conf ${D}/usr/lib/sysusers.d/iot2050-node-red-control.conf
    install -m 644 ${WORKDIR}/tmpfiles.conf ${D}/usr/lib/tmpfiles.d/iot2050-node-red-control.conf
}

do_prepare_build:append() {
    cat <<'EOF' >> ${S}/debian/rules

override_dh_installsystemd:
	dh_installsystemd --no-enable --no-start
EOF
}
