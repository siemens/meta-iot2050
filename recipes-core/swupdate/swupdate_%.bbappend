#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

# Set pacakge build options
# pkg.swupdate.bpo: Avoid mtd read errors during swupdate processing
DEB_BUILD_PROFILES += "pkg.swupdate.bpo"
