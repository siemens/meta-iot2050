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

CERT_DIR=/etc/iot2050/web-gateway
CERT_FILE="$CERT_DIR/tls.crt"
KEY_FILE="$CERT_DIR/tls.key"
HOST_NAME="$(hostname -f 2>/dev/null || hostname)"

if [ -s "$CERT_FILE" ] && [ -s "$KEY_FILE" ]; then
	exit 0
fi

mkdir -p "$CERT_DIR"

SAN="DNS:localhost,IP:127.0.0.1"

if [ -n "$HOST_NAME" ] && [ "$HOST_NAME" != "localhost" ]; then
	SAN="$SAN,DNS:$HOST_NAME"
fi

for ADDRESS in $(hostname -I 2>/dev/null || true); do
	SAN="$SAN,IP:$ADDRESS"
done

openssl req \
	-x509 \
	-newkey rsa:4096 \
	-nodes \
	-sha256 \
	-days 3650 \
	-keyout "$KEY_FILE" \
	-out "$CERT_FILE" \
	-subj "/CN=$HOST_NAME" \
	-addext "subjectAltName=$SAN" >/dev/null 2>&1

chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"
