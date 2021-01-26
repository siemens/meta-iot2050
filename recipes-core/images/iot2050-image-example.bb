#
# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Su Baocheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-core/images/iot2050-image-base.bb

DESCRIPTION = "IOT2050 Debian Example Image"

DEPENDS += "openssl"

# debug tools
IOT2050_DEBIAN_DEBUG_PACKAGES = " \
    busybox \
    bash-completion \
    less \
    vim \
    psmisc \
    bsdmainutils \
    nano \
    ifupdown \
    iputils-ping \
    ssh \
    pciutils \
    usbutils \
    ethtool \
    rt-tests \
    stress-ng \
    build-essential \
    python3 \
    gawk \
    curl \
    wget \
    ca-certificates \
    resolvconf \
    python3-newt \
    gdb \
    gdbserver \
    network-manager \
    modemmanager \
    ppp \
    isc-dhcp-client \
    cmake \
    autoconf \
    autotools-dev \
    default-jdk \
    mosquitto \
    mosquitto-clients \
    nodejs \
    npm \
    teamd \
    rsyslog \
    net-tools \
    i2c-tools \
    sudo \
    "

# wifi support
IOT2050_DEBIAN_WIFI_PACKAGES = " \
    iw \
    wpasupplicant \
    firmware-ath9k-htc \
    firmware-atheros \
    firmware-brcm80211 \
    firmware-iwlwifi \
    firmware-libertas \
    firmware-ralink \
    firmware-realtek \
    firmware-ti-connectivity \
    "

# bluetooth support
IOT2050_DEBIAN_BT_PACKAGES = " \
    bluez \
    pulseaudio-module-bluetooth \
    "
# alsa support
IOT2050_DEBIAN_ALSA_PACKAGES = " \
    alsa-utils \
    alsa-tools \
    "
IMAGE_PREINSTALL += " \
    ${IOT2050_DEBIAN_DEBUG_PACKAGES} \
    ${IOT2050_DEBIAN_WIFI_PACKAGES} \
    ${IOT2050_DEBIAN_BT_PACKAGES} \
    ${IOT2050_DEBIAN_ALSA_PACKAGES} \
    "

IMAGE_INSTALL += " \
    expand-on-first-boot \
    sshd-regen-keys \
    regen-rootfs-uuid \
    customizations-example \
    switchserialmode \
    iot2050setup \
    iot2050-firmware-update \
    tcf-agent \
    mraa \
    node-red \
    node-red-gpio \
    node-red-dashboard \
    node-red-contrib-opcua \
    node-red-contrib-modbus \
    node-red-contrib-s7 \
    mindconnect-node-red-contrib-mindconnect \
    node-red-node-serialport \
    node-red-node-sqlite \
    "
