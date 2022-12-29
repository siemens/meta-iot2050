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

NPM_LOCAL_INSTALL_DIR ?= "/root/.node-red"
