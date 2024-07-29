# Copyright (c) Siemens AG, 2018-2024
#
# SPDX-License-Identifier: MIT
inherit dpkg-raw

NPMPN ?= "${PN}"
NPM_SHRINKWRAP ?= "file://npm-shrinkwrap.json.nodev"
PKG_INSTALL_DIR ?= "/srv"
NPM_INSTALL_FLAGS ?= ""

NPM_REBUILD ?= "1"

ISAR_CROSS_COMPILE = "0"
SBUILD_FLAVOR = "npm"

def get_sources(d, srcdir):
    all_src = []
    files_dir = os.path.join(d.getVar('THISDIR'), 'files')
    src_dir = os.path.join(files_dir, srcdir)
    for path, subdirs, files in os.walk(src_dir):
        for name in files:
            all_src.append(os.path.join(path, name))
    all_src.sort()
    return ' '.join(['file://' + s[len(files_dir)+1:] for s in all_src])

SRC_URI_PKG = " \
    ${@get_sources(d, 'src')} \
    file://.eslintrc.yml \
    file://jsconfig.json \
    file://next.config.js \
    file://package.json \
    ${NPM_SHRINKWRAP} \
    "
SRC_URI = " \
    ${SRC_URI_PKG} \
    file://src \
    file://iot2050-conf-webui.service \
    "
NPM_MAPPED_NAME = "${PN}"
NPM_REGISTRY = "https://registry.npmjs.org"

# function maps arch names to npm arch names
def npm_arch_map(target_arch, d):
    import re
    if   re.match('p(pc|owerpc)(|64)', target_arch): return 'ppc'
    elif re.match('i386$', target_arch): return 'ia32'
    elif re.match('amd64$', target_arch): return 'x64'
    return target_arch

NPM_ARCH ?= "${@npm_arch_map(d.getVar('DISTRO_ARCH'), d)}"

NPM_CLASS_PACKAGE ?= "npm"
OWN_NPM_CLASS_PACKAGE ?= "0"

DEBIAN_BUILD_DEPENDS =. "${@'python3, libnode108,' if d.getVar('NPM_REBUILD') == '1' else ''}"
DEBIAN_BUILD_DEPENDS =. "${NPM_CLASS_PACKAGE},"
DEBIAN_DEPENDS =. "\${shlibs:Depends}, \${misc:Depends},"

SCHROOT_MOUNTS = "${WORKDIR}"

npm_fetch_do_mounts() {
    schroot_create_configs
    insert_mounts
}

npm_fetch_undo_mounts() {
    remove_mounts
    schroot_delete_configs
}

def get_npm_bundled_tgz(d):
    return "{0}-{1}-bundled.tgz".format(d.getVar('NPM_MAPPED_NAME'),
                                        d.getVar('PV'))

def runcmd(d, cmd):
    import subprocess

    chrootcmd = "schroot -c {0} -- {1}".format(d.getVar('SBUILD_CHROOT'), cmd)
    bb.note("Running " + chrootcmd)
    (retval, output) = subprocess.getstatusoutput(chrootcmd)
    if retval:
        bb.fatal("Failed to run '{0}'{1}".format(
            cmd, (":\n" + output) if output else ""))
    bb.note(output)

def apply_mirrors_in_shrinkwrap(path, pattern, subst):
    import json, re
    with open(path, 'r') as f:
        data = json.load(f)
    for pname, pdef in data['packages'].items():
        if 'resolved' in pdef:
            pdef['resolved'] = re.sub(pattern, subst, pdef['resolved'])
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

python fetch_npm() {
    import json, os, shutil, re

    workdir = d.getVar('WORKDIR')
    tmpdir = workdir + "/fetch-tmp"
    tmppkgdir = tmpdir + "/package"
    os.mkdir(tmppkgdir)
    shrinkwarp_url = d.getVar('NPM_SHRINKWRAP')
    pkg_src_uri = d.getVar('SRC_URI_PKG').split()

    try:
        fetch = bb.fetch2.Fetch([shrinkwarp_url], d)
        fetch.unpack(workdir)
    except bb.fetch2.BBFetchException as e:
        bb.fatal(str(e))

    shrinkwarp_path = fetch.localpath(shrinkwarp_url)

    filelist = ' '.join([fetch.localpath(u) + ":True" for u in pkg_src_uri])
    checksum_list = bb.fetch2.get_file_checksums(filelist, d.getVar('PN'), [])
    checksum_list = [f'{f} {c}' for f, c in checksum_list]
    checksum_list.sort()

    bundled_tgz = d.getVar('DL_DIR') + "/" + get_npm_bundled_tgz(d)
    bundled_tgz_hash = bundled_tgz + ".hash"

    fetch_hash = "\n".join([f"{d.getVar('PN')}_{d.getVar('PV')}", *checksum_list])

    if os.path.exists(bundled_tgz) and os.path.exists(bundled_tgz_hash):
        with open(bundled_tgz_hash) as hash_file:
            hash = hash_file.read()
        if hash == fetch_hash:
            return

    bb.build.exec_func("npm_fetch_do_mounts", d)
    bb.utils.export_proxies(d)

    old_cwd = os.getcwd()
    os.chdir(tmppkgdir)

    shutil.copyfile(shrinkwarp_path, "npm-shrinkwrap.json")

    # changing the home directory to the tmpdir directory, the .npmrc will
    # be created in this directory
    os.environ['HOME'] = d.getVar('PP') + "/fetch-tmp/package"

    # apply simplified PREMIRRORS logic to NPM_REGISTRY and shrinkwrap
    npm_registry = d.getVar('NPM_REGISTRY', True)
    mirrors = bb.fetch2.mirror_from_string(d.getVar('PREMIRRORS'))
    npm_mirrors = filter(lambda m: m[0].startswith('npm://'), mirrors)
    for m in npm_mirrors:
        pattern = m[0].replace('npm://','')
        subst = m[1].replace('npm://','')
        npm_registry = re.sub(pattern, subst, npm_registry)
        apply_mirrors_in_shrinkwrap('npm-shrinkwrap.json', pattern, subst)
    os.environ.update({'npm_config_registry': npm_registry})

    # copy files into fetch-tmp/package
    src_uri = (d.getVar('SRC_URI_PKG', True) or "").split()
    for u in src_uri:
        if u.startswith("file://"):
            filename = os.path.join('./' + u.replace("file://", ""))
            filepath = fetch.localpath(u)
            if not os.path.isdir(filepath):
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                shutil.copyfile(filepath, filename)

    package_filename = "package.json"
    with open(package_filename) as infile:
        json_objs = json.load(infile)

    # Must remove devDependencies, maybe npm issue?
    devDependencies = json_objs.get('devDependencies')
    if devDependencies:
        json_objs.pop('devDependencies')

    with open(package_filename, 'w') as outfile:
        json.dump(json_objs, outfile, indent=2)

    runcmd(d, "npm ci --install-strategy=shallow --ignore-scripts --verbose")

    with open(package_filename) as infile:
        json_objs = json.load(infile)

    dependencies = json_objs.get('dependencies')
    if dependencies:
        json_objs.update({'bundledDependencies': [d for d in dependencies]})

    # update package.json so that all dependencies are bundled
    with open(package_filename, 'w') as outfile:
        json.dump(json_objs, outfile, indent=2)

    runcmd(d, "tar czf ../package.tgz --exclude .bin --exclude .npm ../package")
    shutil.copyfile("../package.tgz", bundled_tgz)

    with open(bundled_tgz_hash, 'w') as hash_file:
        hash_file.write(fetch_hash)

    os.chdir(old_cwd)
    bb.build.exec_func("npm_fetch_undo_mounts", d)
}
do_fetch[postfuncs] += "fetch_npm"
do_fetch[cleandirs] += "${WORKDIR}/fetch-tmp"
do_fetch[depends] += "${SCHROOT_DEP}"

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
    mkdir -p ${D}/${PKG_INSTALL_DIR}

    # install service
    install -v -d ${D}/lib/systemd/system/
    install -v -m 644 ${WORKDIR}/iot2050-conf-webui.service ${D}/lib/systemd/system/
}

do_prepare_build:append() {
    INSTALL_FLAGS="--offline --omit=dev --no-package-lock --verbose \
                   --arch=${NPM_ARCH} --target_arch=${NPM_ARCH} \
                   --no-audit"

    CHDIR=${PP}/image/${PKG_INSTALL_DIR}
    # Must be installed as global style, maybe a npm issue?
    INSTALL_FLAGS="$INSTALL_FLAGS --prefix ${CHDIR} -g"

    if [ -n "${NPM_REBUILD}" ]; then
        INSTALL_FLAGS="$INSTALL_FLAGS --build-from-source --no-save"
    fi

    cat <<EOF >> ${S}/debian/rules

export HOME=${PP}
export npm_config_cache=${PP}/npm_cache

override_dh_clean:
	rm -rf ${CHDIR}/lib
	rm -rf ${CHDIR}/${NPMPN}
	rm -rf $(npm_config_cache)

override_dh_auto_build:
	cd ${CHDIR} && npm install ${INSTALL_FLAGS} ${NPM_INSTALL_FLAGS} /downloads/${@get_npm_bundled_tgz(d)}
	mv ${CHDIR}/lib/node_modules/${NPMPN} ${CHDIR}/${NPMPN}
	rm -rf ${CHDIR}/lib
	npm run build --prefix ${CHDIR}/${NPMPN}

# disable slow stripping - not enough value for our ad-hoc npm packaging
override_dh_strip_nondeterminism:
EOF
}
