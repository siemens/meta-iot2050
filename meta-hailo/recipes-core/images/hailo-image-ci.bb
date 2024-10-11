# SPDX-FileCopyrightText: Copyright 2024 Siemens AG
# SPDX-License-Identifier: MIT
inherit image

DESCRIPTION = "CI test image for HAILO"

IMAGE_INSTALL += " \
    hailo-pci-${KERNEL_NAME} \
    hailo-firmware \
    hailortcli \
    python3-hailort \
"
