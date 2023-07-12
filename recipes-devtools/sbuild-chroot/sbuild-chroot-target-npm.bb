DESCRIPTION = "Isar sbuild/schroot filesystem for target (npm variant)"

require recipes-devtools/sbuild-chroot/sbuild-chroot-target.bb

SBUILD_FLAVOR = "npm"
SBUILD_CHROOT_PREINSTALL_EXTRA ?= "npm dpkg-dev"
