#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Su Baocheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-core/images/iot2050-image-base.bb
require recipes-core/images/iot2050-package-selections.inc

DESCRIPTION = "IOT2050 Debian Example Image"

IMAGE_PREINSTALL += " \
    ${IOT2050_DEBIAN_DEBUG_PACKAGES} \
    ${IOT2050_DEBIAN_WIFI_PACKAGES} \
    ${IOT2050_DEBIAN_BT_PACKAGES} \
    ${IOT2050_DEBIAN_ALSA_PACKAGES} \
    ${IOT2050_DEBIAN_MULTIARCH_PACKAGES} \
    "

IOT2050_DOCKER_SUPPORT ?= "0"

IMAGE_PREINSTALL += "${@ ' \
    ${IOT2050_DEBIAN_DOCKER_PACKAGES} \
    ' if d.getVar('IOT2050_DOCKER_SUPPORT') == '1' else ''}"

IMAGE_INSTALL += " \
    expand-on-first-boot \
    sshd-regen-keys \
    regen-rootfs-uuid \
    install-on-emmc \
    customizations-example \
    switchserialmode \
    iot2050-firmware-update \
    tcf-agent \
    mraa \
    ${@ 'board-conf-tools' if d.getVar('QEMU_IMAGE') != '1' else '' } \
    libteec1 \
    optee-client-dev \
    tee-supplicant \
    iot2050-event-record \
    "

IOT2050_NODE_RED_SUPPORT ?= "1"

IMAGE_INSTALL += "${@ ' \
    node-red \
    node-red-gpio \
    node-red-preinstalled-nodes \
    ' if d.getVar('IOT2050_NODE_RED_SUPPORT') == '1' else ''}"

IOT2050_EIO_SUPPORT ?= "0"

IMAGE_INSTALL += "${@ ' \
    iot2050-eio-manager \
    iot2050-conf-webui \
    ' if d.getVar('IOT2050_EIO_SUPPORT') == '1' else ''}"

IOT2050_MODULE_FWU ?= "0"
IMAGE_INSTALL += "${@ ' \
    iot2050-module-firmware-update \
    ' if d.getVar('IOT2050_MODULE_FWU') == '1' else '' }"
