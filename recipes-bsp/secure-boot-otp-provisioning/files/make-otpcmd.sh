#!/bin/sh
#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Baocheng Su <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT

set -e

usage()
{
	printf "%b" "Usage: $0 provision ITSFILE KEYFILE1 KEYFILE2 [KEYFILE3]\n"
	printf "%b" "       $0 switch ITSFILE KEYFILE1 KEYFILE2\n"
	printf "%b" "\nPositional arguments:\n"
	printf "%b" "provision\t\tMake the otpcmd data for key provisioning "\
				"and secure boot enabling.\n"
	printf "%b" "switch\t\t\tMake the otpcmd data for switching the "\
				"current effective key.\n"
	printf "%b" "ITSFILE\t\tThe its file.\n"
	printf "%b" "KEYFILE1\t\tThe first private key in pem format.\n"
	printf "%b" "KEYFILE2\t\tThe second private key in pem format.\n"
	printf "%b" "\nOptional arguments:\n"
	printf "%b" "KEYFILE3\t\tThe third private key in pem format. "\
				"No need to provide it for key switching\n"

	exit 1
}

# Generate x509 Template
X509_TEMPLATE=x509-template.txt
gen_template()
{
[ -f "$X509_TEMPLATE" ] && rm $X509_TEMPLATE
cat << 'EOF' > $X509_TEMPLATE
[ req ]
distinguished_name     = req_distinguished_name
x509_extensions        = v3_ca
prompt                 = no
dirstring_type         = nobmp

[ req_distinguished_name ]
C                      = CN
ST                     = Sichuan
L                      = Chengdu
O                      = Siemens AG
OU                     = SEWC
CN                     = Siemens AG
emailAddress           = IOT2000.industry@siemens.com

[ v3_ca ]
basicConstraints       = CA:true
1.3.6.1.4.1.294.1.3    = ASN1:SEQUENCE:swrv
1.3.6.1.4.1.294.1.34   = ASN1:SEQUENCE:sysfw_image_integrity
1.3.6.1.4.1.294.1.35   = ASN1:SEQUENCE:sysfw_image_load

[ swrv ]
swrv = INTEGER:0

[ sysfw_image_integrity ]
shaType                = OID:2.16.840.1.101.3.4.2.3
shaValue               = FORMAT:HEX,OCT:TEST_IMAGE_SHA_VAL
imageSize              = INTEGER:TEST_IMAGE_LENGTH

[ sysfw_image_load ]
destAddr = FORMAT:HEX,OCT:fffffffe
authInPlace = INTEGER:2
EOF
}

case "$1" in
	provision)
		[ $# -gt 3 ] || usage
		shift 1
		ITS=$1
		shift 1
		KEY1=$1
		shift 1
		KEY2=$1
		if [ $# -gt 1 ]; then
			shift 1
			KEY3=$1
		fi
		;;
	switch)
		[ $# -eq 4 ] || usage
		shift 1
		ITS=$1
		shift 1
		KEY1=$1
		shift 1
		KEY2=$1
		KEY_SWITCH=y
		;;
	*)
		usage
		;;
esac

[ -f "$ITS" ] || { echo "[$ITS] does not exist!"; exit 1; }
[ -f "$KEY1" ] || { echo "KEY1 [$KEY1] does not exist!"; exit 1; }
[ -f "$KEY2" ] || { echo "KEY2 [$KEY2] does not exist!"; exit 1; }
[ -z "$KEY3" ] || [ -f "$KEY3" ] || { echo "KEY3 [$KEY3] does not exist!"; exit 1; }

if [ -z "$KEY_SWITCH" ]; then
	KEY1_HASH=key1.sha256
	KEY2_HASH=key2.sha256
	KEY3_HASH=key3.sha256
	openssl rsa -in $KEY1 -pubout -outform der | openssl dgst -sha256 -binary -out $KEY1_HASH
	openssl rsa -in $KEY2 -pubout -outform der | openssl dgst -sha256 -binary -out $KEY2_HASH
	[ -f "$KEY3" ] && openssl rsa -in $KEY3 -pubout -outform der | openssl dgst -sha256 -binary -out $KEY3_HASH
fi

FIT_IMAGE=target.fit
mkimage -f $ITS $FIT_IMAGE

if [ -z "$KEY_SWITCH" ]; then
	rm $KEY1_HASH $KEY2_HASH
	[ -f "$KEY3_HASH" ] && rm $KEY3_HASH
fi

sign_image()
{
	KEY=$1
	IMAGE=$2
	IMAGE_SIGNED=$3

	TEMP_X509=x509-temp.cert

	SHA_VAL=`openssl dgst -sha512 -hex $IMAGE | sed -e "s/^.*= //g"`
	BIN_SIZE=`cat $IMAGE | wc -c`

	gen_template

	sed -e "s/TEST_IMAGE_LENGTH/$BIN_SIZE/"	\
		-e "s/TEST_IMAGE_SHA_VAL/$SHA_VAL/" $X509_TEMPLATE > $TEMP_X509
	
	openssl req -new -x509 -key $KEY -nodes -outform DER -out $IMAGE.cert -config $TEMP_X509 -sha512
	
	cat $IMAGE.cert $IMAGE > $IMAGE_SIGNED
	
	rm $TEMP_X509 $IMAGE.cert $IMAGE $X509_TEMPLATE
}

OTPCMD=otpcmd.bin
sign_image $KEY1 $FIT_IMAGE $OTPCMD

if [ -n "$KEY_SWITCH" ]; then
	mv $OTPCMD $OTPCMD.1st
	sign_image $KEY2 $OTPCMD.1st $OTPCMD
fi
