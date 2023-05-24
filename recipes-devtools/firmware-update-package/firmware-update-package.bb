#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
DESCRIPTION = "Generate The Firmware Update Package"
MAINTAINER = "huaqian.li@siemens.com"

SRC_URI = "file://iot2050-generate-fwu-tarball.sh \
           file://update.conf.json.tmpl"

addtask create_tarball after do_deploy before do_build

do_create_tarball[depends] += "u-boot-iot2050:do_deploy"

do_create_tarball() {
    cp -rf ${THISDIR}/files/* ${WORKDIR}

    # Generate the firmware update package
    sh ${WORKDIR}/iot2050-generate-fwu-tarball.sh ${WORKDIR} \
		${DEPLOY_DIR_IMAGE} $(${ISAR_RELEASE_CMD})
}
