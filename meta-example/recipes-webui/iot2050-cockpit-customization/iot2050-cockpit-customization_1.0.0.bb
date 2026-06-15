#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 Cockpit customization (issue banner, branding, SM marker)"

DEBIAN_DEPENDS = "cockpit, systemd, network-manager"
DEBIAN_REPLACES = "cockpit-ws, cockpit"

SRC_URI = " \
    file://update-issue \
    file://90-iot2050-cockpit-issue-update \
    file://50-iot2050-banner.conf \
    file://cockpit-issue.service.d/override.conf \
    file://cockpit.socket.d/override.conf \
    file://iot2050-board-marker.service \
    file://postinst \
    file://branding.css \
    "

do_install() {
    # --- Issue banner ---
    install -d -m 755 ${D}/usr/lib/iot2050/cockpit
    install -m 755 ${WORKDIR}/update-issue ${D}/usr/lib/iot2050/cockpit/update-issue

    install -d -m 755 ${D}/usr/lib/NetworkManager/dispatcher.d
    install -m 755 ${WORKDIR}/90-iot2050-cockpit-issue-update ${D}/usr/lib/NetworkManager/dispatcher.d/

    install -d -m 755 ${D}/etc/systemd/system/cockpit-issue.service.d
    install -m 644 ${WORKDIR}/cockpit-issue.service.d/override.conf ${D}/etc/systemd/system/cockpit-issue.service.d/

    install -d -m 755 ${D}/etc/systemd/system/cockpit.socket.d
    install -m 644 ${WORKDIR}/cockpit.socket.d/override.conf ${D}/etc/systemd/system/cockpit.socket.d/

    # --- SSH login banner ---
    # sshd reads /etc/ssh/sshd_config.d/*.conf before the main sshd_config.
    # Drop-in `50-iot2050-banner.conf` sets `Banner /etc/issue.net` so that
    # the issue.net file (managed by update-issue) is displayed before login.
    install -d -m 755 ${D}/etc/ssh/sshd_config.d
    install -m 644 ${WORKDIR}/50-iot2050-banner.conf ${D}/etc/ssh/sshd_config.d/

    # --- SM board marker ---
    install -d -m 755 ${D}/usr/lib/systemd/system
    install -m 644 ${WORKDIR}/iot2050-board-marker.service ${D}/usr/lib/systemd/system/

    # --- Branding ---
    # cockpit-ws serves branding.css from /usr/share/cockpit/branding/<variant>/.
    # Install into both debian and default variants so the override is always
    # applied regardless of distro-id lookup.
    install -d -m 755 ${D}/usr/share/cockpit/branding/debian
    install -m 644 ${WORKDIR}/branding.css ${D}/usr/share/cockpit/branding/debian/branding.css

    install -d -m 755 ${D}/usr/share/cockpit/branding/default
    install -m 644 ${WORKDIR}/branding.css ${D}/usr/share/cockpit/branding/default/branding.css
}
