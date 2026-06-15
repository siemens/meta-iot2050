#!/bin/sh
#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

STATE_DIR=/var/lib/iot2050-firstboot-onboarding
COMPLETE_MARKER="$STATE_DIR/complete"
GATEWAY_SELECTOR="/usr/lib/iot2050/web-gateway/iot2050-web-gateway-select-mode"

run_optional() {
	"$@" >/dev/null 2>&1 || echo "Warning: failed to run: $*" >&2
}

[ -f "$COMPLETE_MARKER" ] || exit 0

if [ -x "$GATEWAY_SELECTOR" ]; then
	run_optional "$GATEWAY_SELECTOR" runtime
fi

run_optional systemctl disable iot2050-firstboot-onboarding.service
run_optional systemctl enable cockpit.socket
run_optional systemctl start cockpit.socket
run_optional systemctl start cockpit.service
run_optional systemctl reload-or-restart nginx.service
