# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT

inherit dpkg-raw

DESCRIPTION = "Isolated Node-RED PAM credentials and account management"
DPKG_ARCH = "any"
DEBIAN_BUILD_DEPENDS = "libpam0g-dev"
DEBIAN_DEPENDS = "\${shlibs:Depends}, init-system-helpers, python3, passwd, libpam-modules, libpam-pwquality, cracklib-runtime, wamerican, systemd"

SRC_URI = " \
    file://pam-helper.c \
    file://backend.py \
    file://broker.py \
    file://admin-auth.js \
    file://iot2050-node-red-auth.service \
    file://iot2050-node-red-auth.sysusers \
    file://99-node-red-auth.preset \
    file://postinst \
    file://policy.json \
"

do_install() {
    install -d ${D}/usr/lib/iot2050/node-red-auth
    install -m 600 ${WORKDIR}/backend.py ${WORKDIR}/broker.py ${D}/usr/lib/iot2050/node-red-auth/
    install -m 644 ${WORKDIR}/admin-auth.js ${D}/usr/lib/iot2050/node-red-auth/
    install -d ${D}/etc/iot2050/node-red-auth
    install -m 600 ${WORKDIR}/policy.json ${D}/etc/iot2050/node-red-auth/
    install -d ${D}/usr/lib/systemd/system
    install -m 644 ${WORKDIR}/iot2050-node-red-auth.service ${D}/usr/lib/systemd/system/
    install -d ${D}/usr/lib/sysusers.d
    install -m 644 ${WORKDIR}/iot2050-node-red-auth.sysusers ${D}/usr/lib/sysusers.d/iot2050-node-red-auth.conf
    install -d ${D}/usr/lib/systemd/system-preset
    install -m 644 ${WORKDIR}/99-node-red-auth.preset ${D}/usr/lib/systemd/system-preset/
}

do_prepare_build:append() {
    cp ${WORKDIR}/pam-helper.c ${S}/pam-helper.c
    cat <<'EOF' >> ${S}/debian/rules

export DEB_BUILD_MAINT_OPTIONS = hardening=+all
DEB_HOST_GNU_TYPE ?= $(shell dpkg-architecture -qDEB_HOST_GNU_TYPE)
DEB_HOST_MULTIARCH ?= $(shell dpkg-architecture -qDEB_HOST_MULTIARCH)

override_dh_auto_build:
	$(DEB_HOST_GNU_TYPE)-gcc $(shell dpkg-buildflags --get CPPFLAGS) \
		$(shell dpkg-buildflags --get CFLAGS) -Wall -Wextra -Werror \
		pam-helper.c $(shell dpkg-buildflags --get LDFLAGS) -lpam \
		-o image/usr/lib/iot2050/node-red-auth/pam-helper

override_dh_installsystemd:
	dh_installsystemd --no-enable --no-start

# Track dpkg paths, including pre-usrmerge paths in dependency packages.
override_dh_installdeb:
	printf 'interest-noawait %s\n' /usr/lib/$(DEB_HOST_MULTIARCH) \
		/lib/$(DEB_HOST_MULTIARCH) /usr/sbin/unix_chkpwd \
		/usr/sbin/unix_update /usr/sbin/pwhistory_helper /usr/sbin/faillock \
		/sbin/unix_chkpwd /sbin/unix_update /sbin/pwhistory_helper /sbin/faillock \
		> debian/iot2050-node-red-auth.triggers
	dh_installdeb

execute_after_dh_fixperms:
	chmod 600 debian/iot2050-node-red-auth/usr/lib/iot2050/node-red-auth/backend.py \
		debian/iot2050-node-red-auth/usr/lib/iot2050/node-red-auth/broker.py \
		debian/iot2050-node-red-auth/etc/iot2050/node-red-auth/policy.json
	chmod 700 debian/iot2050-node-red-auth/usr/lib/iot2050/node-red-auth/pam-helper
EOF
}
