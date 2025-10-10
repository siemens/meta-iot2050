#
# Copyright (c) Siemens AG, 2025
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#

def get_git_tag_timestamp(d):
    import subprocess
    layerdir = d.getVar('LAYERDIR_meta')
    try:
        result = subprocess.check_output(
            ['git', '-C', layerdir, 'for-each-ref', '--sort=-creatordate',
             '--format=%(creatordate:unix)', 'refs/tags/V*'],
            universal_newlines=True
        ).strip()
        return result.splitlines()[0] if result else '0'
    except Exception as e:
        bb.warn(f"Failed to get Git tag timestamp: {e}")
        return '0'
