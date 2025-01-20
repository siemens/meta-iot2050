# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
# SPDX-FileContributor: Authored by Su Bao Cheng <baocheng.su@siemens.com>

inherit dpkg

DESCRIPTION = "Userspace driver for the proximity sensor of IOT2050"
MAINTAINER = "baocheng.su@siemens.com"

DPKG_ARCH = "arm64"

SRC_URI = "file://src \
    "

S = "${WORKDIR}/src"

DEBIAN_BUILD_DEPENDS =. "libsystemd-dev, libcap-dev,"
DEBIAN_DEPENDS =. "\${shlibs:Depends}, \${misc:Depends}, systemd"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize
}
