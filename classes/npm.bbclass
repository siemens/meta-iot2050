# Copyright (c) Siemens AG, 2018-2019
#
# SPDX-License-Identifier: MIT

# HOWTO generate an npm-shrinkwrap.json:
#   npm install --global-style <my-favorite-package>
#   cp package-lock.json /path/to/recipe/files/npm-shrinkwrap.json

inherit dpkg-raw

NPMPN ?= "${PN}"
NPM_SHRINKWRAP ?= "file://npm-shrinkwrap.json"
NPM_LOCAL_INSTALL_DIR ?= ""

NPM_REBUILD ?= "1"

ISAR_CROSS_COMPILE = "0"

SRC_URI = "npm://registry.npmjs.org;name=${NPMPN};version=${PV} \
    ${NPM_SHRINKWRAP}"

# function maps arch names to npm arch names
def npm_arch_map(target_arch, d):
    import re
    if   re.match('p(pc|owerpc)(|64)', target_arch): return 'ppc'
    elif re.match('i386$', target_arch): return 'ia32'
    elif re.match('amd64$', target_arch): return 'x64'
    return target_arch

NPM_ARCH ?= "${@npm_arch_map(d.getVar('DISTRO_ARCH'), d)}"

NPM_CLASS_PACKAGE ?= "npm"

# needed as gyp from bullseye does not establish /usr/bin/python
DEBIAN_BUILD_DEPENDS =. "${@'python,' if d.getVar('NPM_REBUILD') == '1' else ''}"
DEBIAN_BUILD_DEPENDS =. "${NPM_CLASS_PACKAGE},"

DEBIAN_BUILD_DEPENDS =. "${@'libnode72,' if d.getVar('NPM_REBUILD') == '1' else ''}"

python() {
    src_uri = (d.getVar('SRC_URI', True) or "").split()
    if len(src_uri) == 0:
        return

    new_src_uri = []
    npm_uri = None
    for u in src_uri:
        if u.startswith("npm://"):
            if npm_uri:
                bb.fatal("Only one npm package per recipe supported")
            npm_uri = u
        else:
            new_src_uri.append(u)

    d.setVar('SRC_URI', ' '.join(new_src_uri))
    d.setVar('NPM_URI', npm_uri)

    type, host, path, user, pswd, params = bb.fetch2.decodeurl(npm_uri)

    if params['version'] != d.getVar('PV'):
        bb.fatal("Mismatch between PV and version stored in registry")

    d.setVar('NPM_REGISTRY', "https://" + host)

    mapped_name = params['name']
    if mapped_name.startswith('@'):
        mapped_name = mapped_name[1:].replace('/', '-')
    d.setVar('NPM_MAPPED_NAME', mapped_name)
}

def get_npm_bundled_tgz(d):
    return "{0}-{1}-bundled.tgz".format(d.getVar('NPM_MAPPED_NAME'),
                                        d.getVar('PV'))

def runcmd(d, cmd, dir):
    import subprocess

    chrootcmd = "sh -c 'cd {0}/{1}; {2}'".format(d.getVar('PP'), dir, cmd)
    bb.note("Running " + chrootcmd)
    (retval, output) = subprocess.getstatusoutput(chrootcmd)
    if retval:
        bb.fatal("Failed to run '{0}'{1}".format(
            cmd, (":\n" + output) if output else ""))
    bb.note(output)

python fetch_npm() {
    import json, os, shutil

    workdir = d.getVar('WORKDIR');
    tmpdir = workdir + "/fetch-tmp"
    shrinkwarp_url = d.getVar('NPM_SHRINKWRAP')

    try:
        fetch = bb.fetch2.Fetch([shrinkwarp_url], d)
        fetch.unpack(workdir)
    except bb.fetch2.BBFetchException as e:
        bb.fatal(str(e))

    shrinkwarp_path = fetch.localpath(shrinkwarp_url)
    filelist = shrinkwarp_path + ":True"
    checksum_list = bb.fetch2.get_file_checksums(filelist, d.getVar('PN'), [])
    _, shrinkwarp_chksum = checksum_list[0]

    bundled_tgz = d.getVar('DL_DIR') + "/" + get_npm_bundled_tgz(d)
    bundled_tgz_hash = bundled_tgz + ".hash"

    fetch_hash = d.getVar('NPM_URI') + "\n" + \
        shrinkwarp_url + " " + shrinkwarp_chksum + "\n"

    if os.path.exists(bundled_tgz) and os.path.exists(bundled_tgz_hash):
        with open(bundled_tgz_hash) as hash_file:
            hash = hash_file.read()
        if hash == fetch_hash:
            return

    old_cwd = os.getcwd()
    os.chdir(tmpdir)

    shutil.copyfile(shrinkwarp_path, "npm-shrinkwrap.json")

    # changing the home directory to the tmpdir directory, the .npmrc will
    # be created in this directory
    os.environ['HOME'] = workdir + "/fetch-tmp"

    os.environ.update({'npm_config_registry': d.getVar('NPM_REGISTRY')})

    npmpn = d.getVar('NPMPN')

    with open("package.json", 'w') as outfile:
        json_objs = {'dependencies': { npmpn: '' }}
        json.dump(json_objs, outfile, indent=2)

    runcmd(d, "npm ci --global-style --ignore-scripts --verbose", "fetch-tmp")

    package_filename = "node_modules/" + npmpn + "/package.json"
    with open(package_filename) as infile:
        json_objs = json.load(infile)

    dependencies = json_objs.get('dependencies')
    if dependencies:
        json_objs.update({'bundledDependencies': [d for d in dependencies]})

    # update package.json so that all dependencies are bundled
    with open(package_filename, 'w') as outfile:
        json.dump(json_objs, outfile, indent=2)

    os.rename("node_modules/" + npmpn, "package")

    runcmd(d, "tar czf package.tgz --exclude .bin package", "fetch-tmp")

    shutil.copyfile("package.tgz", bundled_tgz)
    with open(bundled_tgz_hash, 'w') as hash_file:
        hash_file.write(fetch_hash)

    os.chdir(old_cwd)
}
do_fetch[postfuncs] += "fetch_npm"
do_fetch[cleandirs] += "${WORKDIR}/fetch-tmp"

python clean_npm() {
    import os

    bundled_tgz = d.getVar('DL_DIR') + "/" + get_npm_bundled_tgz(d)
    if os.path.exists(bundled_tgz):
        os.remove(bundled_tgz)

    bundled_tgz_hash = bundled_tgz + ".hash"
    if os.path.exists(bundled_tgz_hash):
        os.remove(bundled_tgz_hash)
}
do_cleanall[postfuncs] += "clean_npm"

do_install() {
    # create directories to be installed
    if [ -n "${NPM_LOCAL_INSTALL_DIR}" ]; then
        mkdir -p ${D}/${NPM_LOCAL_INSTALL_DIR}
    else
        mkdir -p ${D}/usr/lib
    fi
}

do_prepare_build_append() {
    INSTALL_FLAGS="--offline --only=production --no-package-lock --verbose \
                   --arch=${NPM_ARCH} --target_arch=${NPM_ARCH}"

    if [ -n "${NPM_LOCAL_INSTALL_DIR}" ]; then
        CHDIR=${PP}/image/${NPM_LOCAL_INSTALL_DIR}
    else
        CHDIR=/
        INSTALL_FLAGS="$INSTALL_FLAGS --prefix ${PP}/image/usr -g"
    fi

    if [ -n "${NPM_REBUILD}" ]; then
        INSTALL_FLAGS="$INSTALL_FLAGS --build-from-source --no-save"
    fi

    cat <<EOF >> ${S}/debian/rules

export HOME=${PP}
export npm_config_cache=${PP}/npm_cache

override_dh_auto_build:
	# ensure empty cache
	rm -rf ${PP}/npm_cache
	cd ${CHDIR} && npm install ${INSTALL_FLAGS} /downloads/${@get_npm_bundled_tgz(d)}
	if [ -n "${NPM_LOCAL_INSTALL_DIR}" ]; then \
	    rm -f ${CHDIR}/node_modules/.package-lock.json; \
	fi

# disable slow stripping - not enough value for our ad-hoc npm packaging
override_dh_strip_nondeterminism:
EOF
}
