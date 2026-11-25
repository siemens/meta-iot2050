# Copyright (c) Siemens AG, 2018-2023
#
# SPDX-License-Identifier: MIT

# HOWTO generate an npm-shrinkwrap.json:
#  - use target Debian version as environment
#  - npm install --install-strategy=shallow <my-favorite-package>
#  - cp package-lock.json /path/to/recipe/files/npm-shrinkwrap.json

inherit dpkg-raw

NPMPN ?= "${PN}"
NPM_SHRINKWRAP ?= "file://npm-shrinkwrap.json"
NPM_LOCAL_INSTALL_DIR ??= ""
NPM_INSTALL_FLAGS ?= ""

NPM_REBUILD ?= "1"

ISAR_CROSS_COMPILE = "0"
SBUILD_FLAVOR = "npm"

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
OWN_NPM_CLASS_PACKAGE ?= "0"

DEBIAN_BUILD_DEPENDS =. "${@'python3, libnode115,' if d.getVar('NPM_REBUILD') == '1' else ''}"
DEBIAN_BUILD_DEPENDS =. "${NPM_CLASS_PACKAGE},"
DEBIAN_DEPENDS =. "\${shlibs:Depends}, \${misc:Depends},"

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

SCHROOT_MOUNTS = "${WORKDIR}"

# unshare mode: sbuild chroot is only available as tarball, unpack it for npm
NPM_CHROOT_DIR = "${WORKDIR}/npm-chroot"
NPM_CHROOT_MOUNTS = "${WORKDIR} ${WORKDIR}:${PP}"

npm_fetch_do_mounts() {
    if [ "${ISAR_CHROOT_MODE}" = "unshare" ]; then
        run_privileged rm -rf ${NPM_CHROOT_DIR}
        mkdir -p ${NPM_CHROOT_DIR}
        run_privileged tar -C ${NPM_CHROOT_DIR} --zstd -xpf ${SBUILD_CHROOT} \
            --exclude='./dev/*'
        run_privileged rm -f ${NPM_CHROOT_DIR}/etc/resolv.conf
        run_privileged cp -L /etc/resolv.conf ${NPM_CHROOT_DIR}/etc/resolv.conf
    else
        schroot_create_configs
        insert_mounts
    fi
}

npm_fetch_undo_mounts() {
    if [ "${ISAR_CHROOT_MODE}" = "unshare" ]; then
        run_privileged rm -rf ${NPM_CHROOT_DIR}
    else
        remove_mounts
        schroot_delete_configs
    fi
}

npm_unshare_run() {
    run_privileged_heredoc <<'EONPM'
        set -e
        # only evaluated in unshare mode, older Isar has no insert_isar_mounts
        ${@insert_isar_mounts(d, d.getVar('NPM_CHROOT_DIR'), d.getVar('NPM_CHROOT_MOUNTS')) if d.getVar('ISAR_CHROOT_MODE') == 'unshare' else ''}
        chroot ${NPM_CHROOT_DIR} /bin/sh -c "cd ${NPM_RUN_CWD} && ${NPM_RUN_CMD}"
EONPM
}

# sbuild in unshare mode does not provide /downloads, which do_dpkg_build needs
sbuild_add_unshare_mounts:append() {
    cat <<'EOF' >> ${SBUILD_CONFIG}
push(@$unshare_bind_mounts, { directory => '${DL_DIR}', mountpoint => '/downloads' });
EOF
}

def get_npm_bundled_tgz(d):
    return "{0}-{1}-bundled.tgz".format(d.getVar('NPM_MAPPED_NAME'),
                                        d.getVar('PV'))

def runcmd(d, cmd):
    import os, subprocess

    if d.getVar('ISAR_CHROOT_MODE') == 'unshare':
        env_vars = ['HOME', 'npm_config_registry',
                    'http_proxy', 'https_proxy', 'no_proxy',
                    'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY']
        env = ' '.join("{0}='{1}'".format(k, os.environ[k])
                       for k in env_vars if k in os.environ)
        d.setVar('NPM_RUN_CWD', os.getcwd())
        d.setVar('NPM_RUN_CMD', 'env {0} {1}'.format(env, cmd))
        bb.note("Running '{0}' in {1}".format(cmd, d.getVar('NPM_CHROOT_DIR')))
        bb.build.exec_func('npm_unshare_run', d)
        return

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

    bb.build.exec_func("npm_fetch_do_mounts", d)
    bb.utils.export_proxies(d)

    old_cwd = os.getcwd()
    os.chdir(tmpdir)

    shutil.copyfile(shrinkwarp_path, "npm-shrinkwrap.json")

    # changing the home directory to the tmpdir directory, the .npmrc will
    # be created in this directory
    os.environ['HOME'] = d.getVar('PP') + "/fetch-tmp"

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

    npmpn = d.getVar('NPMPN')

    with open("package.json", 'w') as outfile:
        json_objs = {'dependencies': { npmpn: '' }}
        json.dump(json_objs, outfile, indent=2)

    runcmd(d, "npm ci --install-strategy=shallow --ignore-scripts --verbose")

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

    runcmd(d, "tar czf package.tgz --exclude .bin package")

    shutil.copyfile("package.tgz", bundled_tgz)
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
    if [ -n "${NPM_LOCAL_INSTALL_DIR}" ]; then
        mkdir -p ${D}/${NPM_LOCAL_INSTALL_DIR}
    else
        mkdir -p ${D}/usr/lib
    fi
}

do_prepare_build:append() {
    INSTALL_FLAGS="--only=production --no-package-lock --verbose \
                   --arch=${NPM_ARCH} --target_arch=${NPM_ARCH} \
                   --no-audit"

    if [ -n "${NPM_LOCAL_INSTALL_DIR}" ]; then
        CHDIR=image${NPM_LOCAL_INSTALL_DIR}
        NODE_MODULES_DIR=${CHDIR}/node_modules
        INSTALL_FLAGS="$INSTALL_FLAGS --offline"
    else
        CHDIR=.
        NODE_MODULES_DIR=image/usr/lib/node_modules
        INSTALL_FLAGS="$INSTALL_FLAGS --prefer-offline  --prefix image/usr -g"
    fi

    if [ -n "${NPM_REBUILD}" ]; then
        INSTALL_FLAGS="$INSTALL_FLAGS --build-from-source --no-save"
    fi

    cat <<EOF >> ${S}/debian/rules

export HOME=\$(CURDIR)
export npm_config_cache=\$(CURDIR)/npm_cache

override_dh_clean:
	rm -rf ${NODE_MODULES_DIR}
	rm -rf \$(npm_config_cache)

override_dh_auto_build:
	cd ${CHDIR} && npm install ${INSTALL_FLAGS} ${NPM_INSTALL_FLAGS} /downloads/${@get_npm_bundled_tgz(d)}
	if [ -n "${NPM_LOCAL_INSTALL_DIR}" ]; then \
		rm -f ${NODE_MODULES_DIR}/.package-lock.json; \
	fi

# disable slow stripping - not enough value for our ad-hoc npm packaging
override_dh_strip_nondeterminism:
EOF
}

