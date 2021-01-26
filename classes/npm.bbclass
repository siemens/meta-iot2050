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

NPM_CLASS_PACKAGE ?= "npm-buildchroot"
OWN_NPM_CLASS_PACKAGE ?= "1"

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
    import os

    uid = os.geteuid()
    gid = os.getegid()
    chrootcmd = "sudo -E chroot --userspec={0}:{1} ".format(uid, gid)
    chrootcmd += d.getVar('BUILDCHROOT_DIR')
    chrootcmd += " sh -c 'cd {0}/{1}; {2}'".format(d.getVar('PP'), dir, cmd)
    bb.note("Running " + chrootcmd)
    (retval, output) = subprocess.getstatusoutput(chrootcmd)
    if retval:
        bb.fatal("Failed to run '{0}'{1}".format(
            cmd, (":\n" + output) if output else ""))
    bb.note(output)

do_install_npm() {
    install_cmd="sudo -E chroot ${BUILDCHROOT_DIR} \
        apt-get install -y -o Debug::pkgProblemResolver=yes \
                --no-install-recommends"

    dpkg_do_mounts

    E="${@ bb.utils.export_proxies(d)}"
    deb_dl_dir_import "${BUILDCHROOT_DIR}"
    sudo -E chroot ${BUILDCHROOT_DIR} \
            apt-get update \
                    -o Dir::Etc::sourcelist="sources.list.d/isar-apt.list" \
                    -o Dir::Etc::sourceparts="-" \
                    -o APT::Get::List-Cleanup="0"
    ${install_cmd} --download-only ${NPM_CLASS_PACKAGE}
    deb_dl_dir_export "${BUILDCHROOT_DIR}"
    ${install_cmd} ${NPM_CLASS_PACKAGE}

    dpkg_undo_mounts
}
do_install_npm[depends] += "${@d.getVarFlag('do_apt_fetch', 'depends')}"
do_install_npm[depends] += "${@(d.getVar('NPM_CLASS_PACKAGE') + ':do_deploy_deb') if d.getVar('OWN_NPM_CLASS_PACKAGE') == '1' else ''}"
do_install_npm[lockfiles] += "${REPO_ISAR_DIR}/isar.lock"

addtask install_npm before do_fetch

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

    bb.build.exec_func("dpkg_do_mounts", d)
    bb.utils.export_proxies(d)

    old_cwd = os.getcwd()
    os.chdir(tmpdir)

    shutil.copyfile(shrinkwarp_path, "npm-shrinkwrap.json")

    # changing the home directory to the tmpdir directory, the .npmrc will
    # be created in this directory
    os.environ['HOME'] = d.getVar('PP') + "/fetch-tmp"

    os.environ.update({'npm_config_registry': d.getVar('NPM_REGISTRY')})

    npmpn = d.getVar('NPMPN')

    with open("package.json", 'w') as outfile:
        json_objs = {'dependencies': { npmpn: '' }}
        json.dump(json_objs, outfile, indent=2)

    runcmd(d, "npm ci --global-style --ignore-scripts --verbose", "fetch-tmp")

    os.chdir("node_modules/" + npmpn)

    with open("package.json") as infile:
        json_objs = json.load(infile)

    dependencies = json_objs.get('dependencies')
    if dependencies:
        json_objs.update({'bundledDependencies': [d for d in dependencies]})

    # update package.json so that all dependencies are bundled
    with open("package.json", 'w') as outfile:
        json.dump(json_objs, outfile, indent=2)

    runcmd(d, "npm pack --ignore-scripts --verbose",
           "fetch-tmp/node_modules/" + npmpn)

    shutil.copyfile("%s-%s.tgz" % (d.getVar('NPM_MAPPED_NAME'), d.getVar('PV')),
                    bundled_tgz)
    with open(bundled_tgz_hash, 'w') as hash_file:
        hash_file.write(fetch_hash)

    os.chdir(old_cwd)
    bb.build.exec_func("dpkg_undo_mounts", d)
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
    dpkg_do_mounts

    # changing the home directory to the working directory, the .npmrc will
    # be created in this directory
    export HOME=${PP}

    # ensure empty cache
    export npm_config_cache=${PP}/npm_cache
    sudo rm -rf ${WORKDIR}/npm_cache

    INSTALL_FLAGS="--offline --only=production --no-package-lock --verbose \
                   --arch=${NPM_ARCH} --target_arch=${NPM_ARCH}"

    if [ -n "${NPM_LOCAL_INSTALL_DIR}" ]; then
        mkdir -p ${D}/${NPM_LOCAL_INSTALL_DIR}
        CHDIR=${PP}/image/${NPM_LOCAL_INSTALL_DIR}
    else
        CHDIR=/
        INSTALL_FLAGS="$INSTALL_FLAGS --prefix ${PP}/image/usr -g"
    fi

    if [ -n "${NPM_REBUILD}" ]; then
        INSTALL_FLAGS="$INSTALL_FLAGS --build-from-source"
    fi

    export CHDIR INSTALL_FLAGS
    sudo -E chroot --userspec=$(id -u):$(id -g) ${BUILDCHROOT_DIR} sh -c ' \
        cd $CHDIR
        npm install $INSTALL_FLAGS /downloads/${@get_npm_bundled_tgz(d)}
    '

    dpkg_undo_mounts
}
