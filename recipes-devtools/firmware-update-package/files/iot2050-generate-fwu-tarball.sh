#!/bin/sh
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#   Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

update_json()
{
    version_letter="$(echo $2 | head -c 1)"
    sed -i '/"version": ".*"/s/"V.*"/"'$2'"/g' $1
    sed -i '/"description": ".*"/s/V.*["$]/'$2\"'/g' $1
    sed -i '/"min_version": ".*"/s/"V/"'$version_letter'/g' $1
}

generate_fwu_tarball()
{
    echo "Generating the firmware tarball..."

    if [ ! -e $2/iot2050-pg1-image-boot.bin ] || \
       [ ! -e $2/iot2050-pg2-image-boot.bin ]; then
        echo "Error: iot2050-pg1/2-image-boot.bin doesn't exist!"
        exit 2
    fi

    if [ ! -e $2/u-boot-initial-env ]; then
        echo "Error: u-boot-initial-env doesn't exist!"
        exit 2
    fi

    mkdir -p $2/.tarball

    cp $1/update.conf.json.tmpl $2/.tarball/update.conf.json
    update_json $2/.tarball/update.conf.json $3
    cp $2/iot2050-pg*-image-boot.bin $2/.tarball
    cp $2/u-boot-initial-env $2/.tarball

    cd $2/.tarball
    tar -cJvf $2/IOT2050-FW-Update-PKG-$3.tar.xz *
    cd - && rm -rf $2/.tarball
}

generate_fwu_tarball $*
