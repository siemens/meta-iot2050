#
# Copyright (c) Siemens AG, 2019-2025
#
# Authors:
#  Su Baocheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
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

IMAGE_PREINSTALL += "${@ ' \
    ${IOT2050_DEBIAN_DOCKER_PACKAGES} \
    ' if d.getVar('IOT2050_DOCKER_SUPPORT') == '1' else ''}"

IMAGE_INSTALL += " \
    expand-on-first-boot \
    sshd-regen-keys \
    regen-rootfs-uuid \
    install-on-emmc \
    iot2050-status-led \
    iot2050-nm-settings \
    nodejs-module-path \
    ssh-root-login \
    change-root-homedir \
    iot2050-switchserialmode \
    iot2050-firmware-update \
    ${@ 'firmware-update-package' if d.getVar('QEMU_IMAGE') != '1' else '' } \
    tcf-agent \
    mraa \
    ${@ 'board-conf-tools' if d.getVar('QEMU_IMAGE') != '1' else '' } \
    libteec1 \
    optee-client-dev \
    linux-headers-${KERNEL_NAME} \
    "

IMAGE_INSTALL += " \
    ${@ d.getVar('IOT2050_META_NODE_RED_PACKAGES') if d.getVar('IOT2050_NODE_RED_SUPPORT') == '1' else ''} \
    ${@ d.getVar('IOT2050_META_SM_PACKAGES')       if d.getVar('IOT2050_SM_SUPPORT')       == '1' else ''} \
    ${@ d.getVar('IOT2050_META_HAILO_PACKAGES')    if d.getVar('IOT2050_HAILO_SUPPORT')    == '1' else ''} \
    "