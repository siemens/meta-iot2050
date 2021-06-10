#
# Copyright (c) Siemens AG, 2019-2021
#
# Authors:
#  Jan Kiszka <jan.kiszka@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

REGULAR_NODE_RED_PACKAGES = " \
    node-red-dashboard \
    node-red-contrib-opcua \
    node-red-contrib-modbus \
    node-red-contrib-s7 \
    node-red-node-serialport \
    node-red-node-sqlite \
    "

NODE_RED_PACKAGES = " \
    ${REGULAR_NODE_RED_PACKAGES} \
    @mindconnect/node-red-contrib-mindconnect"

DEPENDS = " \
    ${REGULAR_NODE_RED_PACKAGES} \
    mindconnect-node-red-contrib-mindconnect"

DEBIAN_DEPENDS = " \
    ${@','.join(d.getVar('REGULAR_NODE_RED_PACKAGES', d).split())}, \
    mindconnect-node-red-contrib-mindconnect"

python do_generate_package_json() {
    import json

    with open(d.getVar('WORKDIR', d) + "/package.json", 'w') as outfile:
        packages = d.getVar('NODE_RED_PACKAGES').split()
        json_objs = {
            'name': 'node-red-project',
            'description': 'A Node-RED Project',
            'version': '0.0.1',
            'private': True,
            'dependencies': { package: '*' for package in packages}
        }
        json.dump(json_objs, outfile, indent=2)
}
addtask generate_package_json before do_install

do_install() {
    install -d ${D}/root/.node-red/
    install -m 0644 ${WORKDIR}/package.json ${D}/root/.node-red/
}
