#!/bin/bash
#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#
# SPDX-License-Identifier: MIT

terminal_resize() {
    local IFS='[;' escape screen_size cols rows
    # detect the size of the screen
    echo -ne '\e7\e[r\e[999;999H\e[6n\e8'
    read -t 5 -sd R escape screen_size || {
        echo Unable to detect the size of the current terminal emulator. >&2
        return 0
    }

    cols="${screen_size##*;}" rows="${screen_size%%;*}"
    if [[ "${cols}" -gt 0 && "${rows}" -gt 0 ]];then
        stty cols "${cols}" rows "${rows}"
    else
        echo Unable to change the size of the current terminal emulator. >&2
        return 0
    fi
}

case $(/usr/bin/tty) in
        /dev/ttyS3)
        terminal_resize
        ;;
esac
