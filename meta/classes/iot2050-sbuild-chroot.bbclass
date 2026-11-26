# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

# Helpers for recipes that fetch or build with the sbuild chroot of isar in both
# the privileged (schroot) and the rootless (unshare) mode.
#
# DL_DIR is available as /downloads in the build chroot. Isar only mounts it
# for schroot.

sbuild_add_unshare_mounts:append() {
    cat <<'EOF' >> ${SBUILD_CONFIG}
push @$unshare_bind_mounts, { directory => '${DL_DIR}', mountpoint => '/downloads' };
EOF
}

# Run commands in the sbuild chroot of a recipe from a python task function,
# with network access and the directories listed in SCHROOT_MOUNTS mounted at
# the same path.
#
# Usage:
#
#   bb.build.exec_func("sbuild_chroot_run_prepare", d)
#   sbuild_chroot_run(d, "npm ci")
#   bb.build.exec_func("sbuild_chroot_run_cleanup", d)

# In unshare mode, the chroot is a tarball that has to be extracted first. It
# contains files owned by sub-ids, so only a privileged session can remove it.
SBUILD_CHROOT_RUN_DIR = "${WORKDIR}/sbuild-chroot-run"
do_fetch[root_cleandirs] += "${SBUILD_CHROOT_RUN_DIR}"

sbuild_chroot_run_prepare() {
    sbuild_chroot_run_prepare_${ISAR_CHROOT_MODE}
}

sbuild_chroot_run_prepare_schroot() {
    schroot_create_configs
    insert_mounts
}

sbuild_chroot_run_prepare_unshare() {
    run_privileged_heredoc <<'EOF'
        set -e
        mkdir -p ${SBUILD_CHROOT_RUN_DIR}
        tar -xf "${SBUILD_CHROOT}" -C ${SBUILD_CHROOT_RUN_DIR}
        # schroot copies the resolver configuration of the host as well
        cp --remove-destination -L /etc/resolv.conf ${SBUILD_CHROOT_RUN_DIR}/etc/resolv.conf
EOF
}

sbuild_chroot_run_cleanup() {
    sbuild_chroot_run_cleanup_${ISAR_CHROOT_MODE}
}

sbuild_chroot_run_cleanup_schroot() {
    remove_mounts
    schroot_delete_configs
}

sbuild_chroot_run_cleanup_unshare() {
    # run in a separate session to ensure nothing is mounted
    run_privileged rm -rf ${SBUILD_CHROOT_RUN_DIR}
}

def sbuild_chroot_run(d, cmd):
    import shlex, subprocess

    bb.note("Running " + cmd)
    if d.getVar('ISAR_CHROOT_MODE') == 'unshare':
        chroot = d.getVar('SBUILD_CHROOT_RUN_DIR')
        # mounts are only visible within the session that creates them
        script = "set -e\n{}\nchroot {} /bin/sh -c {}\n".format(
            insert_isar_mounts(d, chroot, d.getVar('SCHROOT_MOUNTS')),
            chroot, shlex.quote("cd {} && {}".format(shlex.quote(os.getcwd()), cmd)))
        chrootcmd = d.getVar('RUN_PRIVILEGED_CMD') + " /bin/bash -s"
        proc = subprocess.run(chrootcmd.split(), input=script, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval, output = proc.returncode, proc.stdout.strip()
    else:
        chrootcmd = "schroot -c {0} -- {1}".format(d.getVar('SBUILD_CHROOT'), cmd)
        (retval, output) = subprocess.getstatusoutput(chrootcmd)

    if retval:
        bb.fatal("Failed to run '{0}'{1}".format(
            cmd, (":\n" + output) if output else ""))
    bb.note(output)
