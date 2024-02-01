#
# Copyright (c) Siemens AG, 2019-2023
#
# Authors:
#  Torsten Hahn <torsten.hahn.extern@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
cmake_minimum_required(VERSION 3.2)
project(read-rtc-battery)
include_directories(.)
add_executable(readrtcbattery readrtcbattery.c)
set(CMAKE_INSTALL_PREFIX "/usr")
install(TARGETS readrtcbattery RUNTIME DESTINATION bin)
