DESCRIPTION = "Board configuration tool"
MAINTAINER = "nian.gao@siemens.com"

SRC_URI = "file://iot2050setup.py"

DEBIAN_DEPENDS = "python3-newt, mraa"

inherit dpkg-raw

do_install() {
    install -v -d ${D}/usr/bin/
    install -v -m 755 ${WORKDIR}/iot2050setup.py ${D}/usr/bin/iot2050setup
}
