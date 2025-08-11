# Copyright (c) Siemens AG, 2022-2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
#

inherit dpkg

DESCRIPTION = "Secure Boot OTP key provisioning tool"

DEBIAN_BUILD_DEPENDS = "openssl, u-boot-tools, device-tree-compiler"

SRC_URI = " \
    file://its \
    file://keys/custMpk.crt \
    file://keys/custMpk.pem \
    file://keys/custSmpk.crt \
    file://keys/custSmpk.pem \
    file://keys/custBmpk.crt \
    file://keys/custBmpk.pem \
    file://make-otpcmd.sh \
    file://rules.tmpl"

OTPCMD_MODE ?= "provision"
OTPCMD_ITS ?= "its/key-${OTPCMD_MODE}.its"
OTP_MPK ?= "./keys/custMpk.pem"
OTP_SMPK ?= "./keys/custSmpk.pem"
OTP_BMPK ?= ""
OTPCMD_KEYS ?= "${OTP_MPK} ${OTP_SMPK} ${OTP_BMPK}"

TEMPLATE_FILES = "rules.tmpl"
TEMPLATE_VARS += "OTPCMD_MODE OTPCMD_ITS OTPCMD_KEYS"

check_dummy_hash() {
    DUMMY_KEY_HASHES=" \
	    fb337ffb16be62fc4a97e62bf80faab1506b5f6e4231d6fec1dd01429ba016e3 \
	    1e436ba092a4a134102ac68489cf64d5978fb28813d348b94331c98194dd7a09 \
	    fcdf0f123e9a4eba4c8fd4f7b375e110c10fe4c4b916bb800c7a27466c5d791a"

    for key in ${OTPCMD_KEYS}; do
        HASH=`openssl rsa -in ${key} -pubout -outform der 2>/dev/null \
            | openssl dgst -sha256 -binary | hexdump -ve '1/1 "%.2x"'`
        for dummy in ${DUMMY_KEY_HASHES}; do
            if [ "$dummy" = "$HASH" ]; then
                bbwarn "Warning: Dummy key ${key} is used for OTP provisioning!" \
                    "Please make sure this is what you really want!"
            fi
        done
    done
}

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize
    mkdir -p ${S}/its
    cp -rPf ${WORKDIR}/its/* ${S}/its/
    mkdir -p ${S}/keys
    ln -f ${WORKDIR}/keys/* ${S}/keys/
    ln -f ${WORKDIR}/make-otpcmd.sh ${S}
    check_dummy_hash

    echo "otpcmd.bin /usr/lib/secure-boot-otp-provisioning/" > \
            ${S}/debian/secure-boot-otp-provisioning.install
}

dpkg_runbuild:append() {
    # remove keys from source archive
    gunzip ${WORKDIR}/${PN}_${PV}.tar.gz
    tar --delete -f ${WORKDIR}/${PN}_${PV}.tar ${PN}-${PV}/keys
    gzip ${WORKDIR}/${PN}_${PV}.tar
}
