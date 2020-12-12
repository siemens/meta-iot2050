#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
inherit dpkg

DESCRIPTION = "Low Level Skeleton Library for Communication on GNU/Linux platforms"
MAINTAINER = "le.jin@siemens.com"
SRC_URI += "git://github.com/intel-iot-devkit/mraa.git;protocol=https;branch=${MRAA_BRANCH};rev=${MRAA_REV};name=mraa \
            file://${MRAA_BUILD_SWIG30_PATCH_FILE};apply=no \
            file://0001-aio.c-fix-mraa_aio_set_bit-for-result-scaling.patch \
            file://0002-feat-iot2050-add-iot2050-platform-support.patch \
            file://0003-feat-iot2050-add-some-example-code-for-testing.patch \
            file://0004-api-Add-explicit-close-methods-to-classes.patch \
            file://rules"
SRC_URI[sha256sum] = "15783b4c4431a36d44ba95daf134318a04ff44a8190ba3f19abbda89ede35a26"
MRAA_BRANCH = "master"
MRAA_REV = "967585c9ea0e1a8818d2172d2395d8502f6180a2"

S = "${WORKDIR}/git"

MRAA_BUILD_SWIG30_PATCH_FILE = "0001-Add-Node-7.x-aka-V8-5.2-support.patch"
MRAA_BUILD_SWIG30_DIR = "${BUILDCHROOT_DIR}/usr/share/swig3.0"

DEBIAN_BUILD_DEPENDS = " \
    cmake, \
    swig3.0, \
    libpython3-dev, \
    nodejs, \
    libnode-dev, \
    libjson-c-dev, \
    default-jdk:native"

DEBIAN_DEPENDS = "python3, nodejs "

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    deb_debianize
}

# patch swig before build, see https://github.com/intel-iot-devkit/mraa/blob/master/docs/building.md#javascript-bindings-for-nodejs-700
dpkg_runbuild_prepend() {
    if ! sudo -E patch -N -d ${MRAA_BUILD_SWIG30_DIR} -p2 < ${WORKDIR}/${MRAA_BUILD_SWIG30_PATCH_FILE} ; then
        sudo -E patch -R -d ${MRAA_BUILD_SWIG30_DIR} -p2 < ${WORKDIR}/${MRAA_BUILD_SWIG30_PATCH_FILE}
        sudo -E patch -N -d ${MRAA_BUILD_SWIG30_DIR} -p2 < ${WORKDIR}/${MRAA_BUILD_SWIG30_PATCH_FILE}
    fi
}
