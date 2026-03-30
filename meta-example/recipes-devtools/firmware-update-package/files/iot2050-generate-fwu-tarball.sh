#!/bin/bash
#
# Copyright (c) Siemens AG, 2023-2026
#
# Authors:
#   Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

set -e

sign_firmware()
{
    local firmware_bin="$1"
    local worker_env_file="$2"
    local tc_keystore_path="$3"
    local tc_truststore_path="$4"
    local sign_client_bin="$5"
    local dummy_key_path="$6"

    echo "Signing firmware binary: $firmware_bin"

    local hash_file="${firmware_bin}.hash"
    local output_sig="${firmware_bin}.sig"

    if ! command -v openssl >/dev/null 2>&1; then
        echo "Error: openssl not found in PATH."
        exit 1
    fi

    openssl dgst -sha512 -binary -out "$hash_file" "$firmware_bin"

    if [ "$sign_client_bin" = "dummy" ]; then
        echo "Signing with dummy key: $dummy_key_path"
        if [ ! -f "$dummy_key_path" ]; then
            echo "Error: Dummy key file not found at $dummy_key_path" >&2
            exit 1
        fi
        # When using OpenSSL's `pkeyutl` command with the `-sign` option,
        # specifying a digest algorithm (e.g., digest:sha512) instructs OpenSSL
        # to perform the full signature generation process as defined by
        # RSASSA-PKCS1-v1_5. This process includes creating an ASN.1 DER-encoded
        # DigestInfo structure, which bundles the hash algorithm identifier with the
        # actual hash digest, before applying the RSA private key operation.
        openssl pkeyutl -sign -inkey "$dummy_key_path" -pkeyopt digest:sha512 \
            -in "$hash_file" -out "$output_sig"
    else
        if [ -z "$worker_env_file" ] || [ ! -f "$worker_env_file" ]; then
            echo "Error: Worker env file not provided or does not exist: $worker_env_file" >&2
            exit 1
        fi

        if [ -z "$sign_client_bin" ] || [ ! -f "$sign_client_bin" ]; then
            echo "Error: Sign client not provided or does not exist: $sign_client_bin" >&2
            exit 1
        fi

        # Set required env from the worker file
        # shellcheck source=/dev/null
        . "$worker_env_file"

        "$sign_client_bin" signdocument -signrequest \
            -workerid "$TC_WORKER" \
            -infile "$hash_file" \
            -outfile "$output_sig" \
            -host "$TC_HOST" \
            -port "$TC_PORT" \
            -keystore "$tc_keystore_path" \
            -keystorepwd "$TC_KEYSTORE_PASSWD" \
            -truststore "$tc_truststore_path" \
            -truststorepwd "$TC_TRUSTSTORE_PASSWD" \
            -metadata CLIENTSIDE_HASHDIGESTALGORITHM=SHA-512 \
            -metadata USING_CLIENTSUPPLIED_HASH=true
    fi

    rm "$hash_file"
    echo "Signature written to $output_sig"
}

update_json()
{
    sed -i '/"version": ".*"/s/"V.*"/"'"$2"'"/g' "$1"
    sed -i '/"description": ".*"/s/V.*["$]/'"$2"'"/g' "$1"
}

generate_fwu_tarball()
{
    local workdir="$1"
    local release_version="$2"
    local worker_env_file="$3"
    local keystore_path="$4"
    local truststore_path="$5"
    local sign_client_bin="$6"
    local dummy_key_path="$7"

    echo "Generating the firmware tarball..."

    if [ ! -e "$workdir/iot2050-pg1-image-boot.bin" ] || \
       [ ! -e "$workdir/iot2050-pg2-image-boot.bin.fwu" ]; then
        echo "Error: iot2050-pg1-image-boot.bin or iot2050-pg2-image-boot.bin.fwu doesn't exist!"
        exit 2
    fi

    if [ ! -e "$workdir/u-boot-initial-env" ]; then
        echo "Error: u-boot-initial-env doesn't exist!"
        exit 2
    fi

    mkdir -p "$workdir/.tarball"

    cp "$workdir/update.conf.json.tmpl" "$workdir/.tarball/update.conf.json"
    update_json "$workdir/.tarball/update.conf.json" "$release_version"
    cp "$workdir/iot2050-pg1-image-boot.bin" "$workdir/.tarball"
    cp "$workdir/iot2050-pg2-image-boot.bin.fwu" \
        "$workdir/.tarball/iot2050-pg2-image-boot.bin"
    cp "$workdir/u-boot-initial-env" "$workdir/.tarball"

    cd "$workdir/.tarball" || exit
    sign_firmware "iot2050-pg2-image-boot.bin" "$worker_env_file" "$keystore_path" \
        "$truststore_path" "$sign_client_bin" "$dummy_key_path"

    tar -cJvf "$workdir/IOT2050-FW-Update-PKG-$release_version.tar.xz" ./*
    cd - >/dev/null && rm -rf "$workdir/.tarball"
}

generate_fwu_tarball "$@"
