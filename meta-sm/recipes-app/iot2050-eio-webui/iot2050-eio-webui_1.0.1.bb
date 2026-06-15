# Copyright (c) Siemens AG, 2018-2026
#
# SPDX-License-Identifier: MIT

PR = "1"

inherit dpkg-raw

DESCRIPTION = "IOT2050 EIO WebUI Cockpit plugin"

NPMPN ?= "${PN}"
NPM_SHRINKWRAP ?= "file://npm-shrinkwrap.json.nodev"
PKG_INSTALL_DIR ?= "/usr/share/cockpit"
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
    file://manifest.json \
    file://src \
    "

NPM_MAPPED_NAME = "${PN}"
NPM_REGISTRY = "https://registry.npmjs.org"

def npm_arch_map(target_arch, d):
    import re
    if re.match('p(pc|owerpc)(|64)', target_arch):
        return 'ppc'
    elif re.match('i386$', target_arch):
        return 'ia32'
    elif re.match('amd64$', target_arch):
        return 'x64'
    return target_arch

NPM_ARCH ?= "${@npm_arch_map(d.getVar('DISTRO_ARCH'), d)}"

NPM_CLASS_PACKAGE ?= "npm"
OWN_NPM_CLASS_PACKAGE ?= "0"

DEBIAN_BUILD_DEPENDS =. "${@'python3, libnode115,' if d.getVar('NPM_REBUILD') == '1' else ''}"
DEBIAN_BUILD_DEPENDS =. "${NPM_CLASS_PACKAGE},"
DEBIAN_DEPENDS = "cockpit, iot2050-eio-manager, iot2050-cockpit-customization, \${shlibs:Depends}, \${misc:Depends}"

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

    os.environ['HOME'] = d.getVar('PP') + "/fetch-tmp/package"

    npm_registry = d.getVar('NPM_REGISTRY', True)
    mirrors = bb.fetch2.mirror_from_string(d.getVar('PREMIRRORS'))
    npm_mirrors = filter(lambda m: m[0].startswith('npm://'), mirrors)
    for m in npm_mirrors:
        pattern = m[0].replace('npm://','')
        subst = m[1].replace('npm://','')
        npm_registry = re.sub(pattern, subst, npm_registry)
        apply_mirrors_in_shrinkwrap('npm-shrinkwrap.json', pattern, subst)
    os.environ.update({'npm_config_registry': npm_registry})

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
        json_objs.update({'bundledDependencies': [dep for dep in dependencies]})

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
    mkdir -p ${D}${PKG_INSTALL_DIR}
}

do_prepare_build:append() {
    install -m 644 ${WORKDIR}/manifest.json ${S}/manifest.json
    install -m 644 ${WORKDIR}/src/app/icon-siemens.svg ${S}/icon-siemens.svg

    INSTALL_FLAGS="--offline --omit=dev --no-package-lock --verbose \
                   --arch=${NPM_ARCH} --target_arch=${NPM_ARCH} \
                   --no-audit"

    CHDIR=image${PKG_INSTALL_DIR}
    INSTALL_FLAGS="$INSTALL_FLAGS --prefix . -g"

    if [ -n "${NPM_REBUILD}" ]; then
        INSTALL_FLAGS="$INSTALL_FLAGS --build-from-source --no-save"
    fi

    cat <<EOF >> ${S}/debian/rules

export HOME=${PP}
export npm_config_cache=${PP}/npm_cache

override_dh_clean:
	rm -rf ${CHDIR}/lib
	rm -rf ${CHDIR}/${NPMPN}
	rm -rf ${CHDIR}/${NPMPN}.static
	rm -rf \
		${S}/node_modules ${S}/out ${S}/.next \
			${PP}/npm_cache

override_dh_auto_build:
	cd ${CHDIR} && npm install ${INSTALL_FLAGS} ${NPM_INSTALL_FLAGS} /downloads/${@get_npm_bundled_tgz(d)}
	mv ${CHDIR}/lib/node_modules/${NPMPN} ${CHDIR}/${NPMPN}
	rm -rf ${CHDIR}/lib
	npm run build --prefix ${CHDIR}/${NPMPN}

override_dh_auto_install:
	install -d ${CHDIR}/${NPMPN}.static
	cp -a ${CHDIR}/${NPMPN}/out/. ${CHDIR}/${NPMPN}.static/
	install -m 644 manifest.json ${CHDIR}/${NPMPN}.static/
	install -m 644 icon-siemens.svg ${CHDIR}/${NPMPN}.static/icon-siemens.svg
	rm -rf ${CHDIR}/${NPMPN}
	mv ${CHDIR}/${NPMPN}.static ${CHDIR}/${NPMPN}

override_dh_strip_nondeterminism:
EOF
}
