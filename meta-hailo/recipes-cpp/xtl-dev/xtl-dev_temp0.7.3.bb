SUMMARY = "Xtl: Basic tools (containers, algorithms) used by other quantstack packages"
HOMEPAGE = "https://github.com/xtensor-stack/xtl"

inherit dpkg

SRC_URI = "https://github.com/xtensor-stack/xtl.git;protocol=https;branch=master"
SRCREV = "46f8a9390db2c52aaf41de8f93ed0dab97af012d"
SRC_URI += " \
    file://debian/control \
    file://debian/rules \
"

S = "${WORKDIR}/git"

DEPENDS += " libhello "
PROVIDES += "xtl-dev"

DEB_BUILD_PROFILES = "nocheck"
DEB_BUILD_OPTIONS = "nocheck"

do_prepare_build[cleandirs] += "${S}/debian"
do_prepare_build() {
    deb_debianize
    rm -f ${S}/debian/compat
    cp ${WORKDIR}/debian/control \
       ${WORKDIR}/debian/rules \
       ${S}/debian/
}