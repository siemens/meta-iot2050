# Central feature toggle definitions for IoT2050
# SPDX-License-Identifier: MIT
# This file intentionally carries only variable declarations (no logic).

IOT2050_DOCKER_SUPPORT       ?= "0"
IOT2050_NODE_RED_SUPPORT     ?= "0"
IOT2050_SM_SUPPORT           ?= "0"
IOT2050_HAILO_SUPPORT        ?= "0"

IOT2050_DEBIAN_DOCKER_PACKAGES ??= ""
IOT2050_META_NODE_RED_PACKAGES ??= ""
IOT2050_META_SM_PACKAGES ??= ""
IOT2050_META_HAILO_PACKAGES ??= ""