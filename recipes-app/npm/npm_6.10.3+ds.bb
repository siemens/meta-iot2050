inherit dpkg-gbp

SRC_URI = "git://salsa.debian.org/freexian-team/npm.git;protocol=https"
SRCREV = "616a7c023dcb4d98cbb8502b0ce0b54e8997ae6b"

GBP_EXTRA_OPTIONS += "--git-compression=xz"
