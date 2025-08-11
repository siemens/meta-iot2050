#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huqqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
import sys
import time
import os
import textwrap
import psutil
import grpc
from gRPC.EIOManager.iot2050_eio_pb2 import CheckFWURequest
from gRPC.EIOManager.iot2050_eio_pb2_grpc import EIOManagerStub
from iot2050_eio_global import (
    iot2050_eio_api_server
)


def stat_led_toggle():
    with open('/sys/class/leds/status-led-green/brightness', 'w') as green_f, \
        open('/sys/class/leds/status-led-green/trigger', 'w') as green_blink_f, \
        open('/sys/class/leds/status-led-red/brightness', 'w') as red_f:
        green_blink_f.write('none')
        green_blink_f.flush()
        green_f.write('255')
        red_f.write('255')
        green_f.flush()
        red_f.flush()


def broadcast_update_info(message):
    width = 72
    frame = '=' * width
    message = '\n  '.join(textwrap.wrap(message, width))
    prompt = f'''
  {frame}

  {message}
  
  {frame}

Hit the Enter Key to Exit:
    '''
    os.system(f'wall "{prompt}"')


def do_fwu_check():
    with grpc.insecure_channel(iot2050_eio_api_server) as channel:
        stub = EIOManagerStub(channel)
        response = stub.CheckFWU(CheckFWURequest(entity=0))
    return response.status, response.message


def firmware_check():
    status, message = do_fwu_check()
    if status == 0:
        return

    stat_led_toggle()

    # Check the firmware and reminded once on every new session if firmware
    # is not the correct one
    last_sessions = psutil.users()
    while True:
        time.sleep(5)
        current_sessions = psutil.users()
        new_sessions = [s for s in current_sessions if s not in last_sessions]
        if len(new_sessions) > 0:
            broadcast_update_info(message)
        last_sessions = current_sessions

if __name__ == "__main__":
    firmware_check()
    sys.exit(0)
