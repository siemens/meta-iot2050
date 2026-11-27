# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

# Remove private material (e.g. signing keys hard-linked into the source tree
# for sbuild) from the deployed source tarball once the binary packages are
# built, so that it does not end up in source packages users may share.
#
# IOT2050_SOURCE_STRIP_PATHS lists archive members to delete, relative to the
# tarball root, e.g. "${BP}/keys".

IOT2050_SOURCE_STRIP_PATHS ?= ""

# Never store the unstripped source package in the (possibly shared) sstate
# cache.
SSTATE_SKIP_CREATION:task-dpkg-source = "${@'1' if d.getVar('IOT2050_SOURCE_STRIP_PATHS').strip() else '0'}"

iot2050_strip_source_tarball() {
    tarball="${DEPLOY_DIR_SRC}/${DEBIAN_SOURCE}_${PV}.tar.gz"
    if [ -z "${IOT2050_SOURCE_STRIP_PATHS}" ] || [ ! -f "${tarball}" ]; then
        return 0
    fi

    members=""
    for member in ${IOT2050_SOURCE_STRIP_PATHS}; do
        if tar -tzf "${tarball}" "${member}" >/dev/null 2>&1; then
            members="${members} ${member}"
        fi
    done
    if [ -z "${members}" ]; then
        return 0
    fi

    # Rewrite in place: the tarball is hard-linked with the copy in the
    # recipe's source package staging directory, which must be stripped as well.
    tmp="${WORKDIR}/iot2050-strip-source.tar"
    gunzip -c "${tarball}" > "${tmp}"
    tar --delete -f "${tmp}" ${members}
    gzip -n -c "${tmp}" > "${tarball}"
    rm -f "${tmp}"
}

# do_deploy_deb runs after do_dpkg_build, also when the latter is restored from
# sstate while do_dpkg_source was re-executed.
do_deploy_deb[postfuncs] += "iot2050_strip_source_tarball"
do_deploy_deb[lockfiles] += "${DEPLOY_DIR_SRC_LOCK}"
