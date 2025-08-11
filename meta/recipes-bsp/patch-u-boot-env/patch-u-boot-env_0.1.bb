#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

inherit dpkg-raw

DESCRIPTION = "prepare u-boot environment for swupdate"

RDEPENDS += "u-boot-${MACHINE}-config"
DEBIAN_DEPENDS = "libubootenv-tool, u-boot-${MACHINE}-config"

DPKG_ARCH = "all"

SRC_URI += "file://patch-u-boot-env.config \
            file://patch-u-boot-env.sh \
            file://patch-u-boot-env.service"

do_install () {
  install -v -d ${D}/usr/share/u-boot-env
  install -v -m 640 ${WORKDIR}/patch-u-boot-env.config ${D}/usr/share/u-boot-env/patch-u-boot-env.config
  install -v -m 755 ${WORKDIR}/patch-u-boot-env.sh ${D}/usr/share/u-boot-env/patch-u-boot-env.sh
}
