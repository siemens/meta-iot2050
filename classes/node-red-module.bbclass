#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Felix Moessbauer <felix.moessbauer@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

require recipes-app/node-red/node-red-home.inc

# common setting for all node-red-contrib modules
DEBIAN_DEPENDS .= ", node-red"
RDEPENDS += "node-red"

# We need to explicitly set this directory to vendor the dependencies instead
# of using NPMs "global" pattern that shares the dependencies.
# This is required, because we do not model all transitive dependencies as
# as individual debian packages. Modelling all transitive dependencies as
# debian packages is not feasable from a maintenance point of view.
NPM_LOCAL_INSTALL_DIR ?= "/usr/lib"
