#! /usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.

import subprocess
import mraa
import sys
from json_ops.json_ops import BoardConfigurationUtility

board_conf = BoardConfigurationUtility()


def setPinmux(index, mode):
    MODE = mode.upper()
    if 'GPIO' in MODE:
        direction = mode.split('_')[1].lstrip().rstrip().lower()
        pullMode = board_conf.getArduinoPullModeCfg(index)
        pullModeMap = {'Hiz': mraa.MODE_HIZ,
                       'Pull-up': mraa.MODE_PULLUP,
                       'Pull-down': mraa.MODE_PULLDOWN}
        gpio = mraa.Gpio(index)
        gpio.dir(mraa.DIR_OUT if direction == 'output' else mraa.DIR_IN)
        if direction == 'output':
            gpio.write(0)
        gpio.mode(pullModeMap[pullMode])
    elif 'ADC' in MODE or 'PWM' in MODE:
        mraaFuncs = {'ADC': mraa.Aio,
                     'PWM': mraa.Pwm}
        funcName = MODE.split('_')[0].lstrip().rstrip()
        pin = int(MODE.split('_')[1].lstrip().rstrip())
        mraaFuncs[funcName](pin)
    elif 'I2C_SDA' in MODE:
        mraa.I2c(0)
    elif 'SPI_SS' in MODE:
        mraa.Spi(0)
    elif 'UART_RX' in MODE:
        mraa.Uart(0)
    elif 'UART_CTS' in MODE:
        uart = mraa.Uart(0)
        uart.setFlowcontrol(False, True)


def initAruinoPins():
    for i in range(0, 20):
        pinmux = board_conf.getArduinoPinmuxCfg(i)
        if pinmux in board_conf.arduinoPinmuxMap(i):
            setPinmux(i, pinmux)
        else:
            sys.stderr.write("Arduino init pinmux error:" + pinmux)


def initExternalSerialMode():
    initMode = board_conf.getExternalDB9InitMode()
    currentMode = board_conf.getExternalDB9CurrenttMode()
    terminate = board_conf.getExternalRs485TerminalteConf()

    if initMode != currentMode:
        board_conf.setExternalDB9CurrentMode(initMode)
        board_conf.saveConfig()

    terminateOpt = ''
    if (initMode == 'RS485') or (initMode == 'RS422'):
        terminateOpt = ' -t' if terminate == 'on' else ''
    subprocess.call("switchserialmode -m " +
                    initMode + terminateOpt, shell=True)


def main():
    initExternalSerialMode()
    initAruinoPins()


if __name__ == '__main__':
    main()
