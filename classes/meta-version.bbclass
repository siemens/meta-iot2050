# Copyright (c) Siemens AG, 2019
#
# Authors:
#  Le Jin <le.jin@siemens.com>
#
# SPDX-License-Identifier: MIT

get_meta_version() {
    version=$(git describe --long --tag --dirty --always || echo unknown)
    echo $version
}
