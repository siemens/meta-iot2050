#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
inherit dpkg-raw

DESCRIPTION = "IOT2050 Extended IO Manager"
MAINTAINER = "baocheng.su@siemens.com"

SRC_URI = "file://bin/iot2050-eiofsd \
    file://gRPC/EIOManager/iot2050_eio_pb2_grpc.py \
    file://gRPC/EIOManager/iot2050_eio_pb2.py \
    file://gRPC/EIOManager/iot2050_eio_pb2.pyi \
    file://gRPC/EIOManager/iot2050-eio.proto \
    file://iot2050_eio_global.py \
    file://iot2050-eio-service.py \
    file://iot2050-eiod.service \
    file://iot2050-eiofsd.service \
    "

DEBIAN_DEPENDS = "python3, python3-grpcio, python3-dotenv"

do_install() {
    install -v -d ${D}/usr/lib/
    install -v -d ${D}/usr/lib/iot2050/

    install -v -d ${D}/usr/lib/iot2050/eio
    install -v -d ${D}/usr/lib/iot2050/eio/gRPC
    install -v -d ${D}/usr/lib/iot2050/eio/gRPC/EIOManager
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050_eio_pb2_grpc.py ${D}/usr/lib/iot2050/eio/gRPC/EIOManager/
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050_eio_pb2.py ${D}/usr/lib/iot2050/eio/gRPC/EIOManager/
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050_eio_pb2.pyi ${D}/usr/lib/iot2050/eio/gRPC/EIOManager/
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050-eio.proto ${D}/usr/lib/iot2050/eio/gRPC/EIOManager/

    install -v -m 755 ${WORKDIR}/iot2050_eio_global.py ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/iot2050-eio-service.py ${D}/usr/lib/iot2050/eio/

    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eiofsd.service ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eiod.service ${D}/lib/systemd/system/

    install -v -d ${D}/usr/bin/
    install -v -m 755 ${WORKDIR}/bin/iot2050-eiofsd ${D}/usr/bin/
    ln -sf ../lib/iot2050/eio/iot2050-eio-service.py ${D}/usr/bin/iot2050-eio-service

    install -v -d ${D}/eiofs
}
