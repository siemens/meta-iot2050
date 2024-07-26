#
# Copyright (c) Siemens AG, 2023-2024
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
inherit dpkg-raw

DESCRIPTION = "IOT2050 Extended IO Manager"
MAINTAINER = "baocheng.su@siemens.com"

SRC_URI = " \
    file://gRPC/EIOManager/iot2050_eio_pb2_grpc.py \
    file://gRPC/EIOManager/iot2050_eio_pb2.py \
    file://gRPC/EIOManager/iot2050_eio_pb2.pyi \
    file://gRPC/EIOManager/iot2050-eio.proto \
    file://iot2050_eio_global.py \
    file://iot2050_eio_config.py \
    file://iot2050_eio_event.py \
    file://iot2050-eio-service.py \
    file://iot2050-eio-time-syncing.py \
    file://iot2050-eio-cli.py \
    file://iot2050-eio-time-syncing.service \
    file://iot2050-eiod.service \
    file://iot2050-eiofsd.service \
    file://iot2050_eio_fwu.py \
    file://iot2050_eio_fwu_monitor.py \
    file://iot2050-eio-fwu-monitor.service \
    "

SRC_URI += " \
    file://config-schema/schema-sm-config.yaml \
    file://config-schema/schema-na.yaml \
    file://config-schema/schema-sm1223-di-dq.yaml \
    file://config-schema/schema-sm1231-ai.yaml \
    file://config-schema/schema-sm1231-rtd.yaml \
    file://config-schema/schema-sm1238-em-480vac.yaml \
    file://config-schema/schema-sm-sens-di.yaml \
    file://config-schema/schema-sm1221-8di.yaml \
    file://config-template/sm-config-example.yaml \
    file://config-template/mlfb-6ES7223-1QH32-0XB0.yaml \
    file://config-template/mlfb-6ES7223-1PL32-0XB0.yaml \
    file://config-template/mlfb-6ES7231-4HF32-0XB0.yaml \
    file://config-template/mlfb-6ES7231-5PD32-0XB0.yaml \
    file://config-template/mlfb-6ES7231-5PF32-0XB0.yaml \
    file://config-template/mlfb-6ES7238-5XA32-0XB0.yaml \
    file://config-template/mlfb-6ES7647-0CM00-1AA2.yaml \
    file://config-template/mlfb-6ES7231-4HD32-0XB0.yaml \
    file://config-template/mlfb-6ES7221-1BF32-0XB0.yaml \
    file://config-template/mlfb-NA.yaml \
    "

SRC_URI_BIN_PREDOWNLOAD = "${@ ' \
    file://bin/iot2050-eiofsd \
    file://bin/map3-fw.bin \
    file://bin/firmware-version ' if d.getVar('IOT2050_EIO_SUPPORT') == '1' else '' } \
    "

SRC_URI += "${SRC_URI_BIN_PREDOWNLOAD}"

DEBIAN_DEPENDS = "python3, python3-grpcio, python3-dotenv, python3-jsonschema, \
python3-yaml, python3-bitstruct, python3-libgpiod, libflashrom1, libflashrom-dev, \
python3-progress, python3-psutil, libfuse2, "

DEBIAN_BUILD_DEPENDS = "libfuse2, libgpiod2"

python do_fetch:prepend() {
    import textwrap
    src_uri_bin = (d.getVar('SRC_URI_BIN_PREDOWNLOAD') or "").split()
    if len(src_uri_bin) == 0:
        return

    try:
        fetcher = bb.fetch2.Fetch(src_uri_bin, d)
        fetcher.checkstatus()
    except bb.fetch2.BBFetchException as e:
        text = textwrap.dedent(f"""\
            {str(e)}
            Please download the EIO binaries from SIOS before building!
            Check the README.md for details.""")
        bb.fatal(text)
}

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
    install -v -m 755 ${WORKDIR}/iot2050_eio_config.py ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/iot2050_eio_event.py ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/iot2050-eio-service.py ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/iot2050-eio-time-syncing.py ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/iot2050_eio_fwu_monitor.py ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/iot2050-eio-cli.py ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/iot2050_eio_fwu.py ${D}/usr/lib/iot2050/eio/

    install -v -m 755 ${WORKDIR}/bin/map3-fw.bin ${D}/usr/lib/iot2050/eio/
    install -v -m 755 ${WORKDIR}/bin/firmware-version ${D}/usr/lib/iot2050/eio/

    install -v -d ${D}/usr/lib/iot2050/eio/schema
    install -v -d ${D}/usr/lib/iot2050/eio/config-template
    install -v -m 644 ${WORKDIR}/config-schema/schema-sm-config.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-schema/schema-na.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-schema/schema-sm1223-di-dq.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-schema/schema-sm1231-ai.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-schema/schema-sm1231-rtd.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-schema/schema-sm1238-em-480vac.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-schema/schema-sm-sens-di.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-schema/schema-sm1221-8di.yaml ${D}/usr/lib/iot2050/eio/schema/
    install -v -m 644 ${WORKDIR}/config-template/sm-config-example.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7223-1QH32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7223-1PL32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7231-4HF32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7231-5PD32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7231-5PF32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7238-5XA32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7647-0CM00-1AA2.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7231-4HD32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-6ES7221-1BF32-0XB0.yaml ${D}/usr/lib/iot2050/eio/config-template/
    install -v -m 644 ${WORKDIR}/config-template/mlfb-NA.yaml ${D}/usr/lib/iot2050/eio/config-template/

    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eio-time-syncing.service ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eiofsd.service ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eiod.service ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-eio-fwu-monitor.service ${D}/lib/systemd/system/

    install -v -d ${D}/usr/bin/
    install -v -m 755 ${WORKDIR}/bin/iot2050-eiofsd ${D}/usr/bin/
    ln -sf ../lib/iot2050/eio/iot2050-eio-time-syncing.py ${D}/usr/bin/iot2050-eio-time-syncing
    ln -sf ../lib/iot2050/eio/iot2050-eio-service.py ${D}/usr/bin/iot2050-eio-service
    ln -sf ../lib/iot2050/eio/iot2050-eio-cli.py ${D}/usr/bin/iot2050-eio
    ln -sf ../lib/iot2050/eio/iot2050_eio_fwu_monitor.py ${D}/usr/bin/iot2050-eio-fwu-monitor

    install -v -d ${D}/eiofs
}
