##
# Copyright (c) Siemens AG, 2025
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
##

SUMMARY = "IoT2050 base feature aggregation meta package"

IOT2050_META_HAILO_PACKAGES ?= " \
    hailo-pci-${KERNEL_NAME} \
    hailo-firmware \
    hailortcli \
    libhailort \
    libhailort-dev \
    libgsthailo \
    libgsthailo-dev \
    python3-hailort \
    hailort \
    libgsthailotools \
    tappas-apps \
    hailo-post-processes \
    tappas-tracers \
    "
