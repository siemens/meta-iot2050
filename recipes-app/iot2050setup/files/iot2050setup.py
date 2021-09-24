#! /usr/bin/python3
#
# Copyright (c) Siemens AG, 2021
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
import traceback
from snack import *
import subprocess
import re
import os
import json
import mraa
from collections import OrderedDict
import sys
import fcntl
import struct
import tty
import termios
import select

class ansicolors:
    clear = '\033[2J'


class TopMenu:
    def __init__(self):
        self.gscreen = SnackScreen()
        self.boardType = subprocess.check_output('grep -a -o -P "IOT2050[\w\s]+" /proc/device-tree/model',
                                                 shell=True).lstrip().rstrip().decode('utf-8')

    def show(self):
        menuItems = [('OS Settings', OsSettingsMenu(self)),
                     ('Networking', NetworkingMenu(self)),
                     ('Software', SoftwareMenu(self)),
                     ('Peripherals', PeripheralsMenu(self))]
        while True:
            action, selection = ListboxChoiceWindow(screen=self.gscreen,
                                                    title='IOT2050 Setup',
                                                    text='',
                                                    items=menuItems,
                                                    buttons=[('Quit', 'quit', 'ESC')])
            if action == 'quit':
                self.close()
                return
            selection.show()

    def close(self):
        self.gscreen.finish()


class OsSettingsMenu:
    def __init__(self, topmenu):
        self.topmenu = topmenu

    def show(self):
        action, selection = ListboxChoiceWindow(screen=self.topmenu.gscreen,
                                                title='OS Settings',
                                                text='',
                                                items=[('Change Hostname', self.changeHostname),
                                                       ('Change Password', self.changePassword),
                                                       ('Change Time Zone', self.changeTimeZone)],
                                                buttons=[('Back', 'back', 'ESC')])

        if action == 'back':
            return
        selection()

    def changeHostname(self):
        currentHostname = subprocess.check_output('hostname').decode('utf-8').lstrip().rstrip()
        action, text = EntryWindow(screen=self.topmenu.gscreen,
                                   title='Change Host Name',
                                   text='',
                                   prompts=[('Host Name:', currentHostname)],
                                   width=70,
                                   entryWidth=50,
                                   buttons=[('OK'), ('Cancel', 'cancel', 'ESC')])
        if action == 'cancel':
            return
        subprocess.call('hostname ' + text[0].lstrip().rstrip(), shell=True)
        with open('/etc/hostname', 'w') as textfile:
            textfile.write(text[0].lstrip().rstrip())

    def changePassword(self):
        self.topmenu.close()
        print(ansicolors.clear)   # Clear console
        subprocess.call('passwd', shell=True)
        exit()

    def changeTimeZone(self):
        self.topmenu.gscreen.suspend()
        subprocess.call('dpkg-reconfigure tzdata', shell=True)
        self.topmenu.gscreen.resume()


class NetworkingMenu:
    def __init__(self, topmenu):
        self.topmenu = topmenu

    def show(self):
        subprocess.call('nmtui', shell=True, stderr=open(os.devnull, 'wb'))


class SoftwareMenu:
    def __init__(self, topmenu):
        self.topmenu = topmenu

    def show(self):
        action, selection = ListboxChoiceWindow(screen=self.topmenu.gscreen,
                                                title='Software',
                                                text='',
                                                items=[('Manage Autostart Options', self.changeAutostart)],
                                                buttons=[('Back', 'back', 'ESC')])
        if action == 'back':
            return
        selection()

    @staticmethod
    def serviceEnabled(service):
        return 'enabled' in subprocess.Popen('systemctl is-enabled %s' % service,
                                             shell=True,
                                             stdout=subprocess.PIPE,
                                             stderr=open(os.devnull, 'wb')).stdout.read().decode('utf-8')

    def changeAutostart(self):
        sshEnabled = SoftwareMenu.serviceEnabled('ssh')
        tcfAgentEnabled = SoftwareMenu.serviceEnabled('tcf-agent')
        mosquittoAutostartEnabled = SoftwareMenu.serviceEnabled('mosquitto')
        noderedAutostartEnabled = SoftwareMenu.serviceEnabled('node-red')
        buttonbar = ButtonBar(screen=self.topmenu.gscreen, buttonlist=[('Ok', 'ok'), ('Cancel', 'cancel', 'ESC')])
        ct = CheckboxTree(height=4, scroll=0)
        ct.append('SSH Server enabled', selected=sshEnabled)
        ct.append('TCF Agent enabled', selected=tcfAgentEnabled)
        ct.append('Autostart Mosquitto Broker', selected=mosquittoAutostartEnabled)
        ct.append('Autostart Node-RED', selected=noderedAutostartEnabled)
        g = GridForm(self.topmenu.gscreen, 'Advanced Options', 1, 2)
        g.add(ct, 0, 0)
        g.add(buttonbar, 0, 1)
        result = g.runOnce()
        if buttonbar.buttonPressed(result) == 'cancel':
            return
        selectedOptions = ct.getSelection()
        sshEnabledNew = 'SSH Server enabled' in selectedOptions
        tcfAgentEnabledNew = 'TCF Agent enabled' in selectedOptions
        mosquittoAutostartEnabledNew = 'Autostart Mosquitto Broker' in selectedOptions
        noderedAutostartEnabledNew = 'Autostart Node-RED' in selectedOptions
        if sshEnabled != sshEnabledNew:
            self.changeServiceSetting('ssh', sshEnabledNew)
        if tcfAgentEnabled != tcfAgentEnabledNew:
            self.changeServiceSetting('tcf-agent', tcfAgentEnabledNew)
        if mosquittoAutostartEnabled != mosquittoAutostartEnabledNew:
            self.changeServiceSetting('mosquitto', mosquittoAutostartEnabledNew)
        if noderedAutostartEnabled != noderedAutostartEnabledNew:
            self.changeServiceSetting('node-red', noderedAutostartEnabledNew)

    def changeServiceSetting(self, name, status):
        if status:
            subprocess.call('systemctl enable ' + name, shell=True, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            subprocess.call('systemctl start ' + name, shell=True, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
        else:
            subprocess.call('systemctl stop ' + name, shell=True, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            subprocess.call('systemctl disable ' + name, shell=True, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))


class PeripheralsMenu:
    def __init__(self, topmenu):
        self.topmenu = topmenu
        self.configureFile = '/etc/board-configuration.json'
        self.config = self.getConfig()

    def show(self):
        while True:
            action, selection = ListboxChoiceWindow(screen=self.topmenu.gscreen,
                                                    title='Peripherals',
                                                    text='',
                                                    items=[('Configure External COM Ports', self.configureExternalSerialMode),
                                                           ('Configure Arduino I/O', self.configureArduinoIoMode)],
                                                    buttons=[('Back', 'back', 'ESC')])
            if action == 'back':
                return
            selection()

    def getConfig(self):
        with open(self.configureFile, 'r') as f:
            config = json.load(f, object_pairs_hook=OrderedDict)
            return config

    def saveConfig(self, jsonSrc):
        with open(self.configureFile, 'w') as f:
            json.dump(jsonSrc, f, indent=4, separators=(',', ': '))

    def pinmuxArray(self, index):
        return self.config['Arduino_pinmux_map']['IO' + str(index)]

    def _pullMode(self, index):
        return self.config['User_configuration']['IO' + str(index) + '_PULL_MODE']

    def pullMode(self, index):
        pullModeMap = {'Hiz': mraa.MODE_HIZ,
                       'Pull-up': mraa.MODE_PULLUP,
                       'Pull-down': mraa.MODE_PULLDOWN}
        return pullModeMap[self._pullMode(index)]

    def _setPinmuxOfUserConfig(self, pinmux, index):
        self.config['User_configuration']['IO' + str(index) + '_MODE'] = pinmux

    def _pinmuxOfUserConfig(self, index):
        return self.config['User_configuration']['IO' + str(index) + '_MODE']

    def setPinmuxOfUserConfig(self, pinmux, index=None):
        if index is not None:
            self._setPinmuxOfUserConfig(pinmux, index)
        else:
            for i in range(0, 20):
                pinmuxes = self.pinmuxArray(i)
                if pinmux in ' '.join(pinmuxes):
                    self._setPullModeOfUserConfig(i, 'Hiz')
                    self._setPinmuxOfUserConfig([n for n in pinmuxes if pinmux in n][0], i)

    def resetPinmuxOfUserConfig(self, pinmux):
        for i in range(0, 20):
            pinmuxes = self.pinmuxArray(i)
            if pinmux in ' '.join(pinmuxes):
                defaultPinmux = pinmuxes[0]
                self._setPinmuxOfUserConfig(defaultPinmux, i)
                self._setPullModeOfUserConfig(i, 'Hiz')
                if 'GPIO' in defaultPinmux:
                    self.setPinmuxToGpio(defaultPinmux, i)
                elif 'IIC_SDA' in defaultPinmux:
                    mraa.I2c(0)

    def setPinmuxToGpio(self, gpioPinmux, index):
            direction = gpioPinmux.split('_')[1].lstrip().rstrip().lower()
            gpio = mraa.Gpio(index)
            gpio.dir(mraa.DIR_OUT if direction == 'output' else mraa.DIR_IN)
            if direction == 'output':
                gpio.write(0)
            gpio.mode(self.pullMode(index))

    def checkPinmuxConfig(self, pinmux, index=None):
        for i in range(0, 20):
            if index is None or index == i:
                if pinmux in self._pinmuxOfUserConfig(i):
                    return 1
        return 0

    def checkPullModeConfig(self, pullmode, index):
        if pullmode in self._pullMode(index):
            return 1
        return 0

    def _setPullModeOfUserConfig(self, index, pullMode):
        self.config['User_configuration']['IO' + str(index) + '_PULL_MODE'] = pullMode

    def getDirection(self, index):
        if self.checkPinmuxConfig('GPIO_Input', index):
            return 'Input'
        elif self.checkPinmuxConfig('GPIO_Output', index):
            return 'Output'
        else:
            return '--'

    def getPullMode(self, index):
        if self.checkPullModeConfig('Pull-down', index):
            return 'Pull-down'
        elif self.checkPullModeConfig('Pull-up', index):
            return 'Pull-up'
        elif self.checkPullModeConfig('Hiz', index):
            return 'Hiz'

    def configureArduinoGpio(self):
        gpioIndex = 0
        dirIndex = 0
        pullmodeIndex = 0
        while True:
            gm = GridForm(self.topmenu.gscreen,    # screen
                         "Enable GPIO",            # title
                         1, 27)                    # 27x1 grid
            g = GridForm(self.topmenu.gscreen,     # screen
                         "Enable GPIO",            # title
                        4, 2)                      # 2x4 grid
            gm.add(Label('Gpio   | Direction | Pull Mode'), 0, 0)
            gm.add(Label('-------+-----------+----------'), 0, 1)
            for i in range(0, 20):
                gpio = 'Gpio{:<3}'.format(str(i))
                direction = ' {:<10}'.format(self.getDirection(i))
                pullmode = ' {:<9}'.format(self.getPullMode(i))
                label = '%s|%s|%s' % (gpio, direction, pullmode)
                gm.add(Label(label), 0, i + 2)
            gm.add(Label(' '), 0, 23)
            lbGpio = Listbox(height = 1, scroll = 0, returnExit = 0, width = 6, border = 0)
            for i in range(0, 20):
                lbGpio.append('Gpio' + str(i), i)
            lbGpio.setCurrent(gpioIndex)
            lbDir = Listbox(height = 1, scroll = 0, returnExit = 0, width = 11, border = 0)
            lbDir.append('Input', 0)
            lbDir.append('Output', 1)
            lbDir.setCurrent(dirIndex)
            lbPullMode = Listbox(height = 1, scroll = 0, returnExit = 0, width = 10, border = 0)
            lbPullMode.append('Hiz', 0)
            lbPullMode.append('Pull-up', 1)
            lbPullMode.append('Pull-down', 2)
            lbPullMode.setCurrent(pullmodeIndex)
            g.add(Label('Gpio:  '), 0, 0)
            g.add(Label('Direction:  '), 1, 0)
            g.add(Label('Pull-Mode: '), 2, 0)
            g.add(lbGpio, 0, 1)
            g.add(lbDir, 1, 1)
            g.add(lbPullMode, 2, 1)
            btnOk = ButtonBar(screen = self.topmenu.gscreen, buttonlist = [('Ok', 1)], compact = 1)
            g.add(btnOk, 3, 1)
            gm.add(g, 0, 24)
            gm.add(Label(' '), 0, 25)
            btnBack = ButtonBar(screen = self.topmenu.gscreen, buttonlist = [('Back', 'back', 'ESC')])
            gm.add(btnBack, 0, 26)
            result = gm.runOnce()
            if btnBack.buttonPressed(result) == 'back':
                return
            def selectedPullMode(item):
                if item == 2:
                    return 'Pull-down'
                elif item == 1:
                    return 'Pull-up'
                elif item == 0:
                    return 'Hiz'
            if btnOk.buttonPressed(result) == 1:
                gpioIndex = lbGpio.current()
                dirIndex = lbDir.current()
                pullmodeIndex = lbPullMode.current()
                if dirIndex == 0: # input
                    self.setPinmuxOfUserConfig('GPIO_Input', gpioIndex)
                    self._setPullModeOfUserConfig(gpioIndex, selectedPullMode(pullmodeIndex))
                    self.setPinmuxToGpio('GPIO_Input', gpioIndex)
                elif dirIndex == 1: # output
                    self.setPinmuxOfUserConfig('GPIO_Output', gpioIndex)
                    self._setPullModeOfUserConfig(gpioIndex, selectedPullMode(pullmodeIndex))
                    self.setPinmuxToGpio('GPIO_Output', gpioIndex)
                self.saveConfig(self.config)

    def configureArduinoI2c(self):
        btnchoicewind = ButtonChoiceWindow(screen=self.topmenu.gscreen,
                                           title='Enable I2C on IO18 & IO19',
                                           text='',
                                           buttons=['Enable', 'Disable', ('Cancel', 'ESC')],
                                           width=40)
        if btnchoicewind == 'cancel':
            return
        elif btnchoicewind == 'enable':
            i2c = mraa.I2c(0)
            self.setPinmuxOfUserConfig('I2C')
        elif (btnchoicewind == 'disable') and self.checkPinmuxConfig('I2C'):
            self.resetPinmuxOfUserConfig('I2C')
        self.saveConfig(self.config)

    def configureArduinoSpi(self):
        btnchoicewind = ButtonChoiceWindow(screen=self.topmenu.gscreen,
                                           title='Enable SPI on IO10-IO13',
                                           text='',
                                           buttons=['Enable', 'Disable', ('Cancel', 'ESC')],
                                           width=40)
        if btnchoicewind == 'cancel':
            return
        elif btnchoicewind == 'enable':
            spi = mraa.Spi(0)
            self.setPinmuxOfUserConfig('SPI')
        elif btnchoicewind == 'disable' and self.checkPinmuxConfig('SPI'):
            self.resetPinmuxOfUserConfig('SPI')
        self.saveConfig(self.config)

    def configureArduinoUart(self):
        ckboxtree = CheckboxTree(height=2, scroll=0)
        ckboxtree.append(text='RX & TX',   item=1, selected=self.checkPinmuxConfig('UART_RX'))
        ckboxtree.append(text='CTS & RTS', item=2, selected=self.checkPinmuxConfig('UART_CTS'))
        buttonbar = ButtonBar(screen=self.topmenu.gscreen, buttonlist=[('Ok', 'ok'), ('Cancel', 'cancel', 'ESC')])
        g = GridForm(self.topmenu.gscreen,      # screen
                     'Enable UART on IO0-IO3',  # title
                      1, 2)                     # 2x1 grid
        g.add(ckboxtree, 0, 0)
        g.add(buttonbar, 0, 1)
        result = g.runOnce()
        if buttonbar.buttonPressed(result) == 'cancel':
            return

        selected = ckboxtree.getSelection()
        if 1 in selected:
            uart = mraa.Uart(0)
            uart.setFlowcontrol(False, True if 2 in selected else False)
            self.setPinmuxOfUserConfig('UART_RX')
            self.setPinmuxOfUserConfig('UART_TX')
            if 2 in selected:
                self.setPinmuxOfUserConfig('UART_CTS')
                self.setPinmuxOfUserConfig('UART_RTS')
            else:
                self.resetPinmuxOfUserConfig('UART_CTS')
                self.resetPinmuxOfUserConfig('UART_RTS')
        else:
            self.resetPinmuxOfUserConfig('UART')
        self.saveConfig(self.config)

    def configureArduinoPwm(self):
        ckboxtree = CheckboxTree(height=6, scroll=0)
        ckboxtree.append(text='PWM 4', item=4, selected=self.checkPinmuxConfig('PWM_4'))
        ckboxtree.append(text='PWM 5', item=5, selected=self.checkPinmuxConfig('PWM_5'))
        ckboxtree.append(text='PWM 6', item=6, selected=self.checkPinmuxConfig('PWM_6'))
        ckboxtree.append(text='PWM 7', item=7, selected=self.checkPinmuxConfig('PWM_7'))
        ckboxtree.append(text='PWM 8', item=8, selected=self.checkPinmuxConfig('PWM_8'))
        ckboxtree.append(text='PWM 9', item=9, selected=self.checkPinmuxConfig('PWM_9'))
        buttonbar = ButtonBar(screen=self.topmenu.gscreen, buttonlist=[('Ok', 'ok'), ('Cancel', 'cancel', 'ESC')])
        g = GridForm(self.topmenu.gscreen,      # screen
                     'Enable PWM on IO4-IO9',   # title
                      1, 2)                     # 1x1 grid
        g.add(ckboxtree, 0, 0)
        g.add(buttonbar, 0, 1)
        result = g.runOnce()
        if buttonbar.buttonPressed(result) == 'cancel':
            return
        selected = ckboxtree.getSelection()
        for n in range(4, 10):
            if n in selected:
                pwm = mraa.Pwm(n)
                self.setPinmuxOfUserConfig('PWM_' + str(n))
            else:
                self.resetPinmuxOfUserConfig('PWM_' + str(n))
        self.saveConfig(self.config)

    def configureArduinoAdc(self):
        ckboxtree = CheckboxTree(height=6, scroll=0)
        ckboxtree.append(text='ADC 0', item=0, selected=self.checkPinmuxConfig('ADC_0'))
        ckboxtree.append(text='ADC 1', item=1, selected=self.checkPinmuxConfig('ADC_1'))
        ckboxtree.append(text='ADC 2', item=2, selected=self.checkPinmuxConfig('ADC_2'))
        ckboxtree.append(text='ADC 3', item=3, selected=self.checkPinmuxConfig('ADC_3'))
        ckboxtree.append(text='ADC 4', item=4, selected=self.checkPinmuxConfig('ADC_4'))
        ckboxtree.append(text='ADC 5', item=5, selected=self.checkPinmuxConfig('ADC_5'))
        buttonbar = ButtonBar(screen=self.topmenu.gscreen, buttonlist=[('Ok', 'ok'), ('Cancel', 'cancel', 'ESC')])
        g = GridForm(self.topmenu.gscreen,                  # screen
                     'Enable ADC on IO14-IO19',   # title
                     1, 2)                                  # 1x1 grid
        g.add(ckboxtree, 0, 0)
        g.add(buttonbar, 0, 1)
        result = g.runOnce()
        if buttonbar.buttonPressed(result) == 'cancel':
            return
        selected = ckboxtree.getSelection()
        for n in range(0, 6):
            if n in selected:
                aio = mraa.Aio(n)
                self.setPinmuxOfUserConfig('ADC_' + str(n))
            else:
                self.resetPinmuxOfUserConfig('ADC_' + str(n))
        self.saveConfig(self.config)

    def configureArduinoIoMode(self):
        while True:
            self.config = self.getConfig()
            ioInfor = ' Pin  | Current    | Pinmux\n -----+------------+-------------------------------------------\n'
            for i in range(0, 20):
                ioInfor += ' IO{:<3}'.format(str(i))
                ioInfor += '| {:<11}'.format(self.config['User_configuration']['IO' + str(i) + '_MODE'])
                ioInfor += '| ' + ' | '.join(self.config['Arduino_pinmux_map']['IO' + str(i)])
                ioInfor += '\n'
            action, selection = ListboxChoiceWindow(screen=self.topmenu.gscreen,
                                                    title='Configure Arduino I/O',
                                                    text=ioInfor,
                                                    items=[('Enable GPIO', self.configureArduinoGpio),
                                                           ('Enable I2C on IO18 & IO19', self.configureArduinoI2c),
                                                           ('Enable SPI on IO10-IO13', self.configureArduinoSpi),
                                                           ('Enable UART on IO0-IO3', self.configureArduinoUart),
                                                           ('Enable PWM on IO4-IO9', self.configureArduinoPwm),
                                                           ('Enable ADC on IO14-IO19', self.configureArduinoAdc)],
                                                    buttons=[('Back', 'back', 'ESC')],
                                                    width=68)
            if action == 'back':
                return
            selection()

    def configureExternalSerialMode(self):
        self.config = self.getConfig()
        modeItems = ['RS232', 'RS485', 'RS422']
        modeAction, modeSelection = ListboxChoiceWindow(screen=self.topmenu.gscreen,
                                                        title='Configure External COM Ports',
                                                        text='Select a mode:',
                                                        items=modeItems,
                                                        buttons=[('Ok', 'ok'), ('Cancel', 'cancel', 'ESC')],
                                                        default=self.currentMode())
        if modeAction == 'cancel':
            return
        switchMode = modeItems[modeSelection]
        self.terminateStatus = ''
        if (switchMode == 'RS485') or (switchMode == 'RS422'):
            self.terminateStatus = self.selectTerminate()
        if self.topmenu.boardType.startswith('IOT2050 Basic'):
            self.setBasicBoard(switchMode)
        elif self.topmenu.boardType.startswith('IOT2050 Advanced'):
            self.setAdvancedBoard(switchMode)
        else:
            return
        terminateOpt = ' -t' if self.terminateStatus == 'on' else ''
        subprocess.call('switchserialmode -m ' + switchMode + terminateOpt, shell=True)
        self.config['User_configuration']['External_Serial_Current_Mode'] = switchMode
        self.saveConfig(self.config)
        subprocess.call('sync', shell=True)
        if self.topmenu.boardType == 'IOT2050 Advanced PG2':
            subprocess.call('switchserialmode -r', shell=True)

    def currentMode(self):
        mode = self.config['User_configuration']['External_Serial_Current_Mode']
        if mode == 'RS232':
            return 0
        elif mode == 'RS485':
            return 1
        elif mode == 'RS422':
            return 2
        return 0

    def setAdvancedBoard(self, mode):
        command = ''
        if mode == 'RS232':
            command = 'switchserialmode cp210x -D cp2102n24 -m gpio -v 0'
        elif mode == 'RS485':
            command = 'switchserialmode cp210x -D cp2102n24 -m RS485 -g 1'
        elif mode == 'RS422':
            command = 'switchserialmode cp210x -D cp2102n24 -m gpio -v 1'
        subprocess.call(command, shell=True)
        self.config['User_configuration']['External_Serial_Init_Mode'] = mode
        if self.terminateStatus == 'on' or self.terminateStatus == 'off':
                self.config['User_configuration']['External_Serial_Terminate'] = self.terminateStatus
        self.saveConfig(self.config)
        if mode == 'RS485':
            self.setRS485SetupHoldTime()
        if self.topmenu.boardType != 'IOT2050 Advanced PG2':
            ButtonChoiceWindow(screen=self.topmenu.gscreen,
                            title='Note',
                            text='You need to power cycle the device for the changes to take effect',
                            buttons=['Ok'])

    def setRS485SetupHoldTime(self):
        command = 'switchserialmode cp210x -D CP2102N24 -d | grep -o -P \"setup-time\\(0x\\w*\\)\" | grep -o -P \"0x\\w*\"'
        setup = subprocess.check_output(command, shell=True).lstrip().rstrip().decode('utf-8').lower()
        command = 'switchserialmode cp210x -D CP2102N24 -d | grep -o -P \"hold-time\\(0x\\w*\\)\" | grep -o -P \"0x\\w*\"'
        hold = subprocess.check_output(command, shell=True).lstrip().rstrip().decode('utf-8').lower()

        disSetup = '0xaa' if int(setup, 0) == 0 else setup
        disHold = '0xaa' if int(hold, 0) == 0 else hold

        action, values = EntryWindow(screen=self.topmenu.gscreen,
                                     title='Set The Setup and Hold Time of RS485 Mode',
                                     text='The setup and hold time will affect the transfer stable in RS485 mode',
                                     prompts=[('Setup (0x00 ~ 0xffff): ', disSetup), ('Hold (0x00 ~ 0xffff): ', disHold)],
                                     width=70,
                                     entryWidth=50,
                                     buttons=[('OK'), ('Cancel', 'cancel', 'ESC')])

        if action == 'cancel':
            return

        command = 'switchserialmode cp210x -D cp2102n24'
        if int(setup, 0) != int(values[0], 0):
            command += ' -s ' + values[0]
        if int(hold, 0) != int(values[1], 0):
            command += ' -o ' + values[1]
        if ('-s' in command) or ('-o' in command):
            subprocess.call(command, shell=True)

    def setBasicBoard(self, mode):
        persistentReturn = ButtonChoiceWindow(screen=self.topmenu.gscreen,
                                              title='Configure Serial Mode',
                                              text='Do you want to make your changes persistent?\n(Mode setting will be kept after reboot.) ',
                                              buttons=[('Yes', 'yes'), ('No', 'no', 'ESC')],
                                              width=40)
        command = 'switchserialmode ttyuart -D /dev/ttyS2 -m ' + mode
        subprocess.call(command, shell=True)
        if persistentReturn == 'yes':
            self.config['User_configuration']['External_Serial_Init_Mode'] = mode
            if self.terminateStatus == 'on' or self.terminateStatus == 'off':
                self.config['User_configuration']['External_Serial_Terminate'] = self.terminateStatus
            self.saveConfig(self.config)

    def currentTerminate(self):
        terminate = self.config['User_configuration']['External_Serial_Terminate']
        if terminate == 'off':
            return 0
        elif terminate == 'on':
            return 1
        else:
            return 0

    def selectTerminate(self):
        default = self.config['User_configuration']['External_Serial_Terminate']
        rdgroup = RadioGroup()
        rda = rdgroup.add(title = 'Turn off terminate resistor', value = 0, default = 0 if self.currentTerminate() else 1)
        rdb = rdgroup.add(title = 'Turn on terminate resistor', value = 1, default = self.currentTerminate())
        buttonbar = ButtonBar(screen=self.topmenu.gscreen, buttonlist=[('Ok', 'ok'), ('Cancel', 'cancel', 'ESC')])
        g = GridForm(self.topmenu.gscreen,
                     'Set the terminate resistor',
                     1, 3)
        g.add(rda, 0, 0)
        g.add(rdb, 0, 1)
        g.add(buttonbar, 0, 2)
        result = g.runOnce()
        if buttonbar.buttonPressed(result) == 'cancel':
            return default
        return 'on' if rdgroup.getSelection() else 'off'


class TerminalResize:
    """
    python3 has get_terminal size, but it doesn't actually query
    the terminal, just trusts current stty settings, which isn't
    useful here.
    """
    @classmethod
    def resize(cls):
        fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
        with open(fd, 'wb+', buffering=0) as ttyfd:
            # Save the terminal state
            fileno = sys.stdin.fileno()
            stty_sav = termios.tcgetattr(sys.stdin)
            fc_sav = fcntl.fcntl(fileno, fcntl.F_GETFL)

            # Turn off echo.
            stty_new = termios.tcgetattr(sys.stdin)
            stty_new[3] = stty_new[3] & ~termios.ECHO
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, stty_new)
            # Getting the size of the actual terminal window
            # Reference:https://wiki.osdev.org/Terminals
            ttyfd.write(b'\033[7\033[r\033[999;999H\033[6n')
            ttyfd.flush()

            # Put stdin into cbreak mode.
            tty.setcbreak(sys.stdin)

            # Nonblocking mode.
            fcntl.fcntl(fileno, fcntl.F_SETFL, fc_sav | os.O_NONBLOCK)

            try:
                while True:
                    r, w, e = select.select([ttyfd], [], [])
                    if r:
                        output = sys.stdin.read()
                        break
            finally:
                # Reset the terminal back to normal cooked mode
                termios.tcsetattr(fileno, termios.TCSAFLUSH, stty_sav)
                fcntl.fcntl(fileno, fcntl.F_SETFL, fc_sav)

            rows, cols = list(map(int, re.findall(r'\d+', output)))

            fcntl.ioctl(ttyfd, termios.TIOCSWINSZ,
                        struct.pack("HHHH", rows, cols, 0, 0))


def main():
    default_console_login = False
    # get the input type
    input_type = os.readlink('/proc/self/fd/0')
    if "ttyS" in input_type or "ttyUSB" in input_type:
        default_console_login = True

    if default_console_login:
        TerminalResize.resize()
        default_console_level = subprocess.check_output('cat /proc/sys/kernel/printk',shell=True).decode('utf-8')[0]
        # Shield KERN_DEBUG KERN_INFO KERN_NOTICE
        subprocess.call('dmesg -n 5', shell=True)

    mainwindow = TopMenu()
    try:
        mainwindow.show()
    except Exception as e:
        mainwindow.close()
        raise e

    # Restore default console level
    if default_console_login:
        subprocess.call('dmesg -n {}'.format(default_console_level), shell=True)

    mainwindow.close()


if __name__ == '__main__':
    main()
