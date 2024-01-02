#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huqqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
import hashlib
import ctypes
import gpiod


class UpgradeError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.err = ErrorInfo

    def __str__(self):
        return self.err


class FlashRomProgrammer():
    def __init__(self, prog_name, prog_param, chip_names):
        self.c_lib = ctypes.CDLL("/usr/lib/aarch64-linux-gnu/libflashrom.so")
        self.flashprog = ctypes.c_void_p()
        self.flashctx = ctypes.c_void_p()
        self.prog_name = ctypes.create_string_buffer(prog_name)
        self.prog_param = ctypes.create_string_buffer(prog_param)
        self.chip_names = ctypes.create_string_buffer(chip_names)

        if self.c_lib.flashrom_programmer_init(ctypes.pointer(self.flashprog),
                                                  self.prog_name,
                                                  self.prog_param):
            raise UpgradeError("Failed to init flashrom programmer!")

        if self.c_lib.flashrom_flash_probe(ctypes.pointer(self.flashctx),
                                              self.flashprog,
                                              self.chip_names):
            raise UpgradeError("Failed to probe flashrom programmer!")

    def write(self, buffer, size):
        if self.c_lib.flashrom_image_write(self.flashctx,
                                              buffer,
                                              size,
                                              None):
            raise UpgradeError("Failed to write from flash!")

    def read(self, firmware, size):
        if self.c_lib.flashrom_image_read(self.flashctx,
                                             firmware,
                                             size):
            raise UpgradeError("Failed to read from flash!")

    def release(self):
        self.c_lib.flashrom_flash_release(self.flashctx)


class EIOFirmware():
    """The EIOFirmware class represents map3 flash operations"""
    # 1 MB in total
    MAP3_FLASH_SIZE_1_MB = 1024 * 1024
    # The first 784 KB
    MAP3_FIRMWARE_SIZE = 784 * 1024
    # The last 32 KB
    MAP3_CERTIFICATE_OFFSET = MAP3_FLASH_SIZE_1_MB - 32 * 1024

    def __init__(self, firmware):
        self.firmware = open(firmware, "rb")

        self.chip = gpiod.Chip("/dev/gpiochip2")
        self.spi_mux_pin = self.chip.get_line(86)
        self.spi_mux_pin.request(consumer='map3', type=gpiod.LINE_REQ_DIR_OUT)

        # Switch SPI Flash to AM65x
        self.spi_mux_pin.set_value(1)

        try:
            self.flash_prog = \
                FlashRomProgrammer(b"linux_spi", b"dev=/dev/spidev1.0",
                                   b"MX25L8005/MX25L8006E/MX25L8008E/MX25V8005")
            self.write_firmware = self.__get_write_firmware()
        except UpgradeError as e:
            raise UpgradeError("EIOFirmware: {}".format(e.err))

    def __get_write_firmware(self):
        read_buffer = ctypes.create_string_buffer(self.MAP3_FLASH_SIZE_1_MB)
        self.flash_prog.read(read_buffer, self.MAP3_FLASH_SIZE_1_MB)

        self.firmware.seek(0)
        write_firmware = self.firmware.read()
        # Firmware and certificate partitions are required, other
        # partitions are reserved.
        write_firmware = write_firmware[:self.MAP3_FIRMWARE_SIZE] \
            + read_buffer[self.MAP3_FIRMWARE_SIZE:self.MAP3_CERTIFICATE_OFFSET] \
            + write_firmware[self.MAP3_CERTIFICATE_OFFSET:]

        return write_firmware

    def write(self):
        """The EIOFirmware can write contents to map3 flash"""
        # Need to readback and save the reserved partions
        try:
            self.flash_prog.write(self.write_firmware,
                                  self.MAP3_FLASH_SIZE_1_MB)
        except UpgradeError as e:
            raise UpgradeError("EIOFirmware: {}".format(e.err))

    def read(self):
        """The EIOFirmware can read contents from map3 flash"""
        read_buffer = ctypes.create_string_buffer(self.MAP3_FLASH_SIZE_1_MB)
        try:
            self.flash_prog.read(read_buffer, self.MAP3_FLASH_SIZE_1_MB)
        except UpgradeError as e:
            raise UpgradeError("EIOFirmware: {}".format(e.err))

        return read_buffer

    def __del__(self):
        self.spi_mux_pin.release()
        if hasattr(self, "flash_prog") and self.flash_prog:
            self.flash_prog.release()
        self.firmware.close()


class FirmwareUpdate():
    """
    The FirmwareUpdate models the firmware updating behavior for all
    firmware update.
    """
    def __init__(self, firmware):
        self.firmwares = {}
        self.firmwares["map3"] = EIOFirmware(firmware)

    def update(self):
        """Update the firmware to the specified flash"""

        for firmware_type in self.firmwares:
            self.firmwares[firmware_type].write()

            content = self.firmwares[firmware_type].write_firmware
            firmware_md5 = self.__get_md5_digest(content)
            content = self.firmwares[firmware_type].read()
            read_out_md5 = self.__get_md5_digest(content)

            if firmware_md5 != read_out_md5:
                raise UpgradeError("Firmware digest verification failed")

    def __get_md5_digest(self, content):
        """Verify the update integrity"""
        md5 = hashlib.md5()

        md5.update(content)

        return md5.hexdigest()


def update_firmware(firmware):
    try:
        FirmwareUpdate(firmware).update()
        return 0, "Firmware upgrade successfully!"
    except UpgradeError as e:
        return 1, e
