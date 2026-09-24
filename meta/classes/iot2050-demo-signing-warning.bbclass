# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

IOT2050_WARN_DEMO_SIGNING_KEYS ?= "0"

python iot2050_warn_demo_signing_keys() {
    if d.getVar("IOT2050_WARN_DEMO_SIGNING_KEYS") != "1":
        return

    bb.warnonce("IOT2050 demo signing keys are in use. "
                "Replace them before production secure-boot signing "
                "or OTP provisioning.")
}