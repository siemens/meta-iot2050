#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require optee-os-iot2050_3.19.0.inc

SRC_URI += "file://control.tmpl"

TEMPLATE_FILES += " control.tmpl"

PROVIDES = "optee-os-tadevkit"

do_replace_debian_control_tmpl() {
    cp -a ${WORKDIR}/control.tmpl ${WORKDIR}/debian/control.tmpl
}

addtask replace_debian_control_tmpl after do_unpack before do_transform_template

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/

    deb_add_changelog

    rm -f ${S}/debian/optee-os-tadevkit.install
    echo "out/arm-plat-${OPTEE_PLATFORM_BASE}/export-ta_${DISTRO_ARCH} /usr/lib/optee-os/" >> \
        ${S}/debian/optee-os-tadevkit.install
}
