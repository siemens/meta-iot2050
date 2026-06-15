#!/bin/sh
#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Zhao Chun Jiao <chunjiao.zhao@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

set -eu

BASE_DIR=/usr/lib/iot2050/web-gateway

"$BASE_DIR/iot2050-web-gateway-ensure-cert.sh"
"$BASE_DIR/iot2050-web-gateway-select-mode" auto --no-reload
