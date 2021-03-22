#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Quirin Gylstorff <quirin.gylstorff@siemens.com>
#
# SPDX-License-Identifier: MIT

# Set pacakge build options
# cross: for crosscompiling
# nodocs: for no documentation
# nocheck: do not build test
# pkg.swupdate.bpo: Avoid mtd read errors during swupdate processing
SWUPDATE_BUILD_PROFILES += "cross nodoc nocheck pkg.swupdate.bpo"
