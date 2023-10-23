#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

inherit dpkg-raw

DESCRIPTION = "IOT2050 Event Record Service"
MAINTAINER = "huaqian.li@siemens.com"

SRC_URI = " \
    file://gRPC/EventInterface/iot2050_event_pb2_grpc.py  \
    file://gRPC/EventInterface/iot2050_event_pb2.py  \
    file://gRPC/EventInterface/iot2050_event_pb2.pyi  \
    file://gRPC/EventInterface/iot2050-event.proto  \
    file://gRPC/EIOManager/iot2050_eio_pb2_grpc.py \
    file://gRPC/EIOManager/iot2050_eio_pb2.py \
    file://gRPC/EIOManager/iot2050_eio_pb2.pyi \
    file://gRPC/EIOManager/iot2050-eio.proto \
    file://iot2050-event-record.py    \
    file://iot2050-event-wdt.py    \
    file://iot2050-event-record.service    \
    file://iot2050-event-record.conf    \
    file://iot2050-event-serve.py    \
    file://iot2050-event-serve.service    \
    file://iot2050_event.py    \
    file://iot2050_event_global.py"

S = "${WORKDIR}/src"

DEBIAN_DEPENDS = "python3-psutil, python3-systemd"

do_install() {
    install -v -d ${D}/usr/lib/iot2050/event/
    install -v -m 755 ${WORKDIR}/iot2050-event-record.py ${D}/usr/lib/iot2050/event/
    install -v -m 755 ${WORKDIR}/iot2050-event-record.conf ${D}/usr/lib/iot2050/event/
    install -v -m 755 ${WORKDIR}/iot2050-event-wdt.py ${D}/usr/lib/iot2050/event/
    install -v -m 755 ${WORKDIR}/iot2050-event-serve.py ${D}/usr/lib/iot2050/event/
    install -v -m 755 ${WORKDIR}/iot2050_event.py ${D}/usr/lib/iot2050/event/
    install -v -m 755 ${WORKDIR}/iot2050_event_global.py ${D}/usr/lib/iot2050/event/
    install -v -d ${D}/usr/lib/iot2050/event/gRPC/EventInterface/
    install -v -m 755 ${WORKDIR}/gRPC/EventInterface/iot2050_event_pb2_grpc.py  \
        ${D}/usr/lib/iot2050/event/gRPC/EventInterface/
    install -v -m 755 ${WORKDIR}/gRPC/EventInterface/iot2050_event_pb2.py  \
        ${D}/usr/lib/iot2050/event/gRPC/EventInterface/
    install -v -m 755 ${WORKDIR}/gRPC/EventInterface/iot2050_event_pb2.pyi  \
        ${D}/usr/lib/iot2050/event/gRPC/EventInterface/
    install -v -m 755 ${WORKDIR}/gRPC/EventInterface/iot2050-event.proto  \
        ${D}/usr/lib/iot2050/event/gRPC/EventInterface/
    install -v -d ${D}/usr/lib/iot2050/event/gRPC/EIOManager/
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050_eio_pb2_grpc.py  \
        ${D}/usr/lib/iot2050/event/gRPC/EIOManager/
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050_eio_pb2.py  \
        ${D}/usr/lib/iot2050/event/gRPC/EIOManager/
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050_eio_pb2.pyi  \
        ${D}/usr/lib/iot2050/event/gRPC/EIOManager/
    install -v -m 755 ${WORKDIR}/gRPC/EIOManager/iot2050-eio.proto  \
        ${D}/usr/lib/iot2050/event/gRPC/EIOManager/

    install -v -d ${D}/usr/bin/
    ln -sf ../lib/iot2050/event/iot2050-event-record.py ${D}/usr/bin/iot2050-event-record
    ln -sf ../lib/iot2050/event/iot2050-event-serve.py ${D}/usr/bin/iot2050-event-serve

    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-event-record.service ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-event-serve.service ${D}/lib/systemd/system/
}
