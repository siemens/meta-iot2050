DESCRIPTION = "Uboot Firmware Update Scripts"
MAINTAINER = "chao.zeng@siemens.com"

SRC_URI = "file://iot2050-firmware-update.py"

inherit dpkg-raw

do_install() {
    install -v -d ${D}/usr/sbin/
    install -v -m 755 ${WORKDIR}/iot2050-firmware-update.py ${D}/usr/sbin/iot2050update
}
