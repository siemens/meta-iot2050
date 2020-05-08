
inherit dpkg

DESCRIPTION = "Tool to switch between the uart0 modes"
MAINTAINER = "nian.gao@siemens.com"

SRC_URI = "file://switchserialmode.c file://CMakeLists.txt"
S = "${WORKDIR}/switchserialmode"

do_prepare_build[cleandirs] += "${S}/debian"

do_prepare_build() {
    cp ${WORKDIR}/switchserialmode.c ${S}/
    cp ${WORKDIR}/CMakeLists.txt ${S}/
    deb_debianize
    sed -i -e 's/Build-Depends: /Build-Depends: cmake, libusb-1.0-0-dev, /g' ${S}/debian/control
}
