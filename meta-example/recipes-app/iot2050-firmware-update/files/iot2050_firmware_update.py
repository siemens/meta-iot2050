#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020-2026
#
# Authors:
#  Chao Zeng <chao.zeng@siemens.com>
#  Jan Kiszka <jan.kiszka@siemens.com>
#  Su Bao Cheng <baocheng.su@siemens.com>
#  Li Hua Qian <huaqian.li@siemens.com>
#
# This file is subject to the terms and conditions of the MIT License.  See
# COPYING.MIT file in the top-level directory.
#
"""
To use this tool, an update package in <firmware-update-package>.tar.xz
format is needed.

The <firmware-update-package>.tar.xz should contain:
  - firmware.bin: The firmware to update, could be more than one.
  - update.conf.json: The update criteria.
  - u-boot-initial-env: Builtin environment
  - firmware.bin.sig: (Optional)The signature file for the firmware.bin

Example of update.conf.json:
{
    "firmware": [
        {
            "description": "IOT2050 PG1 Bootloader Release V01.01.01",
            "name": "iot2050-pg1-image-boot.bin",
            "version": "V01.01.01",
            "type": "uboot",
            "target_boards": [
                "SIMATIC IOT2050-BASIC",
                "SIMATIC IOT2050 Basic",
                "SIMATIC IOT2050-ADVANCED",
                "SIMATIC IOT2050 Advanced"
            ]
        },
        {
            "description": "IOT2050 PG2 Bootloader Release V01.01.01",
            "name": "iot2050-pg2-image-boot.bin",
            "version": "V01.01.01",
            "type": "uboot",
            "target_boards": [
                "SIMATIC IOT2050 Basic PG2",
                "SIMATIC IOT2050 Advanced PG2",
                "SIMATIC IOT2050 Advanced SM"
            ]
        },
    ],
    "target_os": [
        {
            "type": "[optional] Example Image",
            "key": "BUILD_ID",
            "min_version": "V01.01.01"
        },
        {
            "type": "[optional] Industrial OS",
            "key": "VERSION_ID",
            "min_version": "2.1.1"
        }
    ],
    "suggest_preserved_uboot_env": [
        "boot_targets"
    ]
}

There are one or more `firmware` node, each node represents one firmware file
in the tarball and its update control fields, such as which board and which OS
it could be updated upon.

To indicate which board or boards the firmware could be updated upon, use the
mandatory `target_boards` inside the `firmware` node. Possible target boards:
  - PG1 Basic:
      "SIMATIC IOT2050-BASIC", "SIMATIC IOT2050 Basic"
  - PG1 Advanced:
      "SIMATIC IOT2050-ADVANCED", "SIMATIC IOT2050 Advanced"
  - PG2 Basic:
      "SIMATIC IOT2050 Basic PG2"
  - PG2 Advanced:
      "SIMATIC IOT2050 Advanced PG2", "SIMATIC IOT2050 Advanced PG2 Rev"
  - M2 Variant:
      "SIMATIC IOT2050 Advanced M2", "SIMATIC IOT2050 Advanced M2 Rev"

To indicate which OS the firmware could be updated upon, use either the
`target_os` inside the `firmware` node as a local configuration, or use
a global `target_os` outside the `firmware` node as the global configuration.
If both exists, the local one will overwrite the global one.

Either global or local `target_os` is optional, if none exists, the updater
will not check against the OS information.

The `key` and `min_version` field within the `target_os` node will be compared
to the value from `/etc/os-release` on the board. The `key` matches exactly,
and the `min_version` matches the minimal version number.

There are one `suggest_preserved_uboot_env` node, this filed in this node
represent the env variable need to be preserved. there could be multiple
fileds in this node. Besides, there is a control parameter "-p" to add the
preserved list from cli, this would not use the preserved env variable in the
`suggest_preserved_uboot_env` node.
"""

import argparse
import concurrent.futures
import datetime
import fcntl
import glob
import hashlib
import io
import json
import os
import sys
import shutil
import stat
import struct
import subprocess
import tarfile
import textwrap
import tempfile
import uuid
from pathlib import Path
from packaging import version
from abc import ABC, abstractmethod
from ctypes import *
from enum import Enum
from types import SimpleNamespace as Namespace

# Import cryptography modules for signature verification
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from iot2050_firmware_global import (
    DEFAULT_FIRMWARE_DIR,
    DEFAULT_FIRMWARE_PATTERN,
    DEFAULT_MAX_FIRMWARE_SIZE,
    SYSTEM_FIRMWARE_SOCKET_PATH,
)


def _updater_version():
    """Best-effort version of the installed firmware update package.

    The package is installed via dpkg, so query dpkg directly. Falls back to
    "unknown" when the version cannot be determined (e.g. running from a
    source tree without the package installed).
    """
    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Version}", "iot2050-firmware-update"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


__version__ = _updater_version()

DEFAULT_ROLLBACK_DIR = os.path.join(
    os.environ.get("HOME") or os.path.expanduser("~"), ".rollback_fw"
)
DEFAULT_ROLLBACK_TAR = os.path.join(
    DEFAULT_ROLLBACK_DIR, "rollback_backup_fw.tar"
)
DEFAULT_ROLLBACK_METADATA = DEFAULT_ROLLBACK_TAR + ".json"


def resolve_rollback_path(backup_path=None):
    if isinstance(backup_path, (list, tuple)):
        backup_path = backup_path[0] if backup_path else None
    if not backup_path or os.path.abspath(str(backup_path)) == DEFAULT_ROLLBACK_DIR:
        return DEFAULT_ROLLBACK_TAR
    return os.path.join(str(backup_path), ".rollback_fw",
                        "rollback_backup_fw.tar")


def validate_backup_dir(backup_dir, allow_custom=False):
    """Validate an explicit backup root before using it as root."""
    if not backup_dir:
        return None
    if not allow_custom:
        raise ValueError("Custom backup paths are not accepted by this service")

    path = os.path.abspath(str(backup_dir))
    current = Path(path)
    while True:
        try:
            info = current.lstat()
        except FileNotFoundError:
            parent = current.parent
            if parent == current:
                break
            current = parent
            continue
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("The backup path must not contain symbolic links")
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError("The backup path must contain directories only")
        if info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError(
                "The explicit backup path must be root-owned and private"
            )
        parent = current.parent
        if parent == current:
            break
        current = parent
    return path

class ErrorCode(Enum):
    """The ErrorCode class describes the return codes"""
    SUCCESS = 0
    ROLLBACK_SUCCESS = 1
    INVALID_ARG = 2
    BACKUP_FAILED = 3
    ROLLBACK_FAILED = 4
    FLASHING_FAILED = 5
    CANCELED = 6
    INVALID_FIRMWARE = 7
    FAILED = 8
    MISSING_SIGNATURE = 9
    MISSING_PUBLIC_KEY = 10
    BAD_SIGNATURE = 11

class UpgradeError(Exception):
    def __init__(self, ErrorInfo, code=ErrorCode.FAILED.value):
        super().__init__(self)
        self.err = ErrorInfo
        self.code = code

    def __str__(self):
        return self.err

class Firmware():
    """The Firmware class represents flash base operations for all flashes"""
    def __init__(self, firmware):
        if not isinstance(firmware, io.IOBase):
            raise UpgradeError("TypeError: firmware must be a file-like object!")
        self.firmware = firmware

    def __del__(self):
        if hasattr(self, 'firmware'):
            self.firmware.close()
            del self.firmware

    @abstractmethod
    def write(self):
        """An Firmware can be written to flash"""

    @abstractmethod
    def read(self):
        """An Firmware can be read out from flash"""

class MtdDevice():
    def __get_path_type_value(self, path):
        """get the path value"""
        try:
            with open(path, "r") as f:
                return f.read()
        except IOError as e:
            raise UpgradeError("Reading {} failed: {}".format(path, e.strerror))

    def __erase(self, dev, start, nbytes):
        """This function erases flash sectors
        @dev: flash device file descriptor
        @start: start address
        @nbytes: number of bytes to erase
        """
        MEMERASE = 0x40084d02

        ioctl_data = struct.pack('II', start, nbytes)

        try:
            fcntl.ioctl(dev, MEMERASE, ioctl_data)
        except IOError:
            raise UpgradeError("Flash erasing failed")

    def get_mtd_info(self, mtd_num):
        """The uboot ops can get all mtd infos of uboot"""
        ospi_dev_path = "/sys/bus/platform/devices/47040000.spi"
        if os.path.exists(ospi_dev_path + "/spi_master"):
            # kernel 5.9 and later
            spi_dev = os.listdir(ospi_dev_path + "/spi_master")[0]
            mtd_base_path = "{}/spi_master/{}/{}.0/mtd".format(
                ospi_dev_path, spi_dev, spi_dev
            )
        else:
            # kernel 5.8 and earlier
            mtd_base_path = "{}/mtd".format(ospi_dev_path)

        mtd_sys_path = "{}/mtd{}".format(mtd_base_path, mtd_num)
        mtd_name_path = "{}/name".format(mtd_sys_path)
        mtd_size_path = "{}/size".format(mtd_sys_path)
        mtd_erasesize_path = "{}/erasesize".format(mtd_sys_path)

        mtd_dev_path = "/dev/mtd{}".format(mtd_num)
        try:
            mtd_size = int(self.__get_path_type_value(mtd_size_path))
            mtd_erasesize = int(self.__get_path_type_value(mtd_erasesize_path))
            mtd_name = self.__get_path_type_value(mtd_name_path).strip()
        except UpgradeError as e:
            raise UpgradeError(e.err)

        return mtd_dev_path, mtd_size, mtd_erasesize, mtd_name

    def write(self, mtd_dev_path, mtd_size, mtd_erasesize,
                      file_obj, file_size):
        mtd_dev = None
        mtd_pos = 0
        try:
            mtd_dev = os.open(mtd_dev_path, os.O_SYNC | os.O_RDWR)

            while mtd_pos < mtd_size and file_size > 0:
                mtd_content = os.read(mtd_dev, mtd_erasesize)
                firmware_content = file_obj.read(mtd_erasesize)
                padsize = mtd_erasesize - len(firmware_content)
                firmware_content += bytearray([0xff] * padsize)

                if not mtd_content == firmware_content:
                    self.__erase(mtd_dev, mtd_pos, mtd_erasesize)
                    os.lseek(mtd_dev, mtd_pos, os.SEEK_SET)
                    os.write(mtd_dev, firmware_content)

                mtd_pos += mtd_erasesize
                file_size -= mtd_erasesize
        except IOError as e:
            raise UpgradeError("Opening {} failed: {}".format(mtd_dev_path,
                               e.strerror))
        except UpgradeError as e:
            raise UpgradeError(e.err)
        finally:
            if mtd_dev is not None:
                try:
                    os.close(mtd_dev)
                except OSError:
                    pass

        return file_size

    def read(self, mtd_dev_path, mtd_size, mtd_erasesize,
                file_size):
        mtd_in_memory = b''

        try:
            mtd_dev = os.open(mtd_dev_path, os.O_SYNC | os.O_RDONLY)
        except IOError as e:
            raise UpgradeError("Opening {} failed: {}"
                               "".format(mtd_dev_path, e.strerror))

        mtd_pos = 0
        try:
            while mtd_pos < mtd_size and file_size > 0:
                mtd_content = os.read(mtd_dev, mtd_erasesize)
                mtd_pos += mtd_erasesize
                file_size -= mtd_erasesize
                mtd_in_memory += mtd_content
        finally:
            try:
                os.close(mtd_dev)
            except OSError:
                pass

        return mtd_in_memory

class BootloaderFirmware(Firmware):
    """The Bootloader Firmware class represents uboot flash operations"""
    def __init__(self, firmware):
        super().__init__(firmware)
        self.mtd_device = MtdDevice()

    def write(self):
        """The uboot ops can write contents to uboot flash"""
        mtd_num = 0

        self.firmware.seek(0)
        self.firmware.seek(0, os.SEEK_END)
        firmware_size = self.firmware.tell()
        self.firmware_len = firmware_size
        self.firmware.seek(0)

        while True:
            if firmware_size <= 0:
                break

            try:
                mtd_dev_path, mtd_size, mtd_erasesize, mtd_name = \
                    self.mtd_device.get_mtd_info(mtd_num)
                firmware_size = self.mtd_device.write(
                    mtd_dev_path, mtd_size, mtd_erasesize,
                    self.firmware, firmware_size
                )
            except UpgradeError as e:
                raise UpgradeError("BootloaderFirmware: {}".format(e.err))

            mtd_num += 1

    def read(self, firmware_len=0x8c0000):
        mtd_in_memory = b''
        mtd_num = 0
        while True:
            if firmware_len <= 0:
                break

            try:
                mtd_dev_path, mtd_size, mtd_erasesize, mtd_name = \
                    self.mtd_device.get_mtd_info(mtd_num)

                mtd_in_memory += self.mtd_device.read(mtd_dev_path,
                                                      mtd_size,
                                                      mtd_erasesize,
                                                      firmware_len)
            except UpgradeError as e:
                raise UpgradeError("BootloaderFirmware: {}".format(e.err))

            firmware_len -= mtd_size
            mtd_num += 1

        return mtd_in_memory

class EnvFirmware(Firmware):
    """The EnvFirmware class represents env partition operations"""
    def __init__(self, firmware_path, firmware):
        super().__init__(firmware)
        self.firmware_path = firmware_path
        self.mtd_device = MtdDevice()

        mtd_num = 0
        self.env_mtd_num = None
        self.env_bk_mtd_num = None
        # mtd_device is typically less than 20, if one mtd device can't be
        # located in 20 rounds, jump out the loop.
        for mtd_num in range(20):
            try:
                mtd_dev_path, mtd_size, mtd_erasesize, mtd_name = \
                    self.mtd_device.get_mtd_info(mtd_num)
            except UpgradeError as e:
                raise UpgradeError("EnvFirmware: {}".format(e.err))

            if "env" == mtd_name:
                self.env_mtd_num = mtd_num
            if "env.backup" == mtd_name:
                self.env_bk_mtd_num = mtd_num

            if (self.env_mtd_num is not None and
                    self.env_bk_mtd_num is not None):
                break
        else:
            raise UpgradeError("EnvFirmware: No env partition found")

    def write(self):
        """A env firmware can write contents to the env partition"""
        with tempfile.NamedTemporaryFile() as env_default_binary:
            for mtd_num in self.env_mtd_num, self.env_bk_mtd_num:
                try:
                    mtd_dev_path, mtd_size, mtd_erasesize, mtd_name = \
                        self.mtd_device.get_mtd_info(mtd_num)
                    subprocess.run('mkenvimage -s {} -r -o {} {}'.format(
                                   mtd_size,
                                   env_default_binary.name,
                                   self.firmware_path),
                                   check=True, shell=True)
                    with open(env_default_binary.name, "rb") as env_binary:
                        firmware_content = env_binary.read()
                    firmware_size = len(firmware_content)
                    if self.firmware and not self.firmware.closed:
                        self.firmware.close()
                    self.firmware = io.BytesIO(firmware_content)
                    self.firmware.seek(0)
                    firmware_size = self.mtd_device.write(
                        mtd_dev_path, mtd_size, mtd_erasesize,
                        self.firmware, firmware_size
                    )
                    self.firmware.seek(0)
                    if firmware_size > 0:
                        raise UpgradeError("Write env failed")
                except subprocess.CalledProcessError as error:
                    print(error.stdout)
                    raise UpgradeError("EnvFirmware: Run mkenvimage failed")
                except UpgradeError as e:
                    raise UpgradeError("EnvFirmware: {}".format(e.err))

    def read(self):
        """A env firmware can read contents from the env partition"""
        mtd_in_memory = b''
        try:
            mtd_dev_path, mtd_size, mtd_erasesize, mtd_name = \
                self.mtd_device.get_mtd_info(self.env_mtd_num)

            if "env" == mtd_name:
                mtd_in_memory = self.mtd_device.read(mtd_dev_path,
                                                     mtd_size,
                                                     mtd_erasesize,
                                                     mtd_size)
        except UpgradeError as e:
            raise UpgradeError("EnvFirmware: {}".format(e.err))

        return mtd_in_memory

class ForceUpdate():
    def __init__(self, interactor, firmware, firmware_type="uboot"):
        self.firmware = firmware
        self.firmware_type = firmware_type
        self.interactor = interactor

        if self.firmware_type == "uboot":
            try:
                self.firmware_obj = BootloaderFirmware(self.firmware)
            except UpgradeError as e:
                raise UpgradeError(e.err, ErrorCode.INVALID_FIRMWARE.value)
        else:
            raise UpgradeError("Unsupported firmware type!", ErrorCode.INVALID_FIRMWARE.value)

    def update(self):
        print("===================================================")
        print("IOT2050 firmware update started - DO NOT INTERRUPT!")
        print("===================================================")

        self.interactor.progress_bar(info="Updating {}".format(self.firmware_type))
        self.firmware_obj.write()

        firmware_md5 = hashlib.md5()
        self.firmware.seek(0)
        firmware_md5.update(self.firmware.read())

        read_out_md5  = hashlib.md5()
        read_out_md5.update(self.firmware_obj.read())
        self.interactor.progress_bar(start=False)

        if firmware_md5.hexdigest() != read_out_md5.hexdigest():
            raise UpgradeError("Firmware digest verification failed",
               ErrorCode.FLASHING_FAILED.value)

    def backup(self):
        pass

class FirmwareUpdate():
    """
    The FirmwareUpdate models the firmware updating behavior for all IOT2050
    firmware update.
    """
    def __init__(self, tarball, backup_path, interactor,
                rollback=False, reset=False, verify_signature=False):
        self.rollback_fw_tar = self.__resolve_rollback_path(backup_path)
        self.back_fw_path = os.path.dirname(self.rollback_fw_tar)
        self.interactor = interactor
        self.verify_signature = verify_signature
        self._rollback_input = None
        try:
            if rollback:
                if not os.path.exists(self.rollback_fw_tar) or \
                   not tarfile.is_tarfile(self.rollback_fw_tar):
                    raise UpgradeError("No rollback firmware exists",
                                       ErrorCode.ROLLBACK_FAILED.value)
                tarball = open(self.rollback_fw_tar, "rb")
                self._rollback_input = tarball
                self.tarball = FirmwareTarball(tarball, interactor, None, False)
            else:
                self.tarball = tarball

            self.firmwares = {}
            for firmware_type in self.tarball.FIRMWARE_TYPES:
                if firmware_type ==  self.tarball.FIRMWARE_TYPES[0]:
                    name = self.tarball.get_file_name(firmware_type)
                    self.firmwares[firmware_type] = BootloaderFirmware(
                        self.tarball.get_file(name)
                    )
                elif firmware_type ==  self.tarball.FIRMWARE_TYPES[1]:
                    if not reset:
                        env_list = self.tarball.get_preserved_uboot_env()
                        env_path, env_binary = \
                            self.tarball.generate_env_firmware(env_list)
                        self.firmwares[firmware_type] = \
                            EnvFirmware(env_path, env_binary)
                    else:
                        self.firmwares[firmware_type] = EnvFirmware(
                            self.tarball.get_file_path(self.tarball.UBOOT_ENV_FILE),
                            self.tarball.get_file(self.tarball.UBOOT_ENV_FILE)
                        )
                elif firmware_type ==  self.tarball.FIRMWARE_TYPES[2]:
                    self.firmwares[firmware_type] = \
                        Firmware(self.tarball.get_file(self.tarball.CONF_JSON))
        except UpgradeError as e:
            raise UpgradeError(e.err, e.code)

    @staticmethod
    def __resolve_rollback_path(backup_path):
        return resolve_rollback_path(backup_path)

    def close(self):
        """Release package files deterministically after a manager task."""
        for firmware in getattr(self, "firmwares", {}).values():
            file_object = getattr(firmware, "firmware", None)
            if file_object and not file_object.closed:
                file_object.close()
        if self._rollback_input and not self._rollback_input.closed:
            self._rollback_input.close()

    def backup(self):
        """Backup the original firmware from flash"""
        print("\nFirmware backup started")
        temporary_path = None
        try:
            os.makedirs(self.back_fw_path, mode=0o700, exist_ok=True)
            os.chmod(self.back_fw_path, 0o700)
            temporary_file = tempfile.NamedTemporaryFile(
                prefix=".rollback_backup_fw.",
                suffix=".tmp",
                dir=self.back_fw_path,
                delete=False,
            )
            temporary_path = temporary_file.name
            temporary_file.close()

            self.interactor.progress_bar(info="Backing up")
            with open(
                "/usr/share/iot2050/fwu/update.conf.json", "r", encoding="utf-8"
            ) as template_file:
                tmpl_json = json.load(template_file)
            for firmware_type in self.firmwares:
                md5_digest = []
                fw_name = self.tarball.get_file_name(firmware_type)

                if self.tarball.FIRMWARE_TYPES[0] == firmware_type:
                    i = 0
                    while i < 2:
                        file_content = self.firmwares[firmware_type].read()
                        md5_digest.append(self.__get_md5_digest(file_content))
                        i += 1
                    fw_name = tmpl_json['firmware'][0]['name']
                elif self.tarball.FIRMWARE_TYPES[1] == firmware_type:
                    file = self.firmwares[firmware_type].firmware
                    file.seek(0)
                    file_content = file.read()
                elif self.tarball.FIRMWARE_TYPES[2] == firmware_type:
                    with open("/sys/firmware/devicetree/base/model", "r") as model_f:
                        target_board = model_f.read().replace("\u0000", "")
                    tmpl_json['firmware'][0]['target_boards'] = target_board
                    file_content = bytes(json.dumps(tmpl_json, indent=4), "utf8")
                else:
                    raise UpgradeError("Wrong Firmware Type!")

                if len(md5_digest) > 0 and md5_digest[0] != md5_digest[1]:
                    raise UpgradeError("Firmware backup failed")

                info = tarfile.TarInfo(fw_name)
                info.size = len(file_content)

                if firmware_type == self.tarball.FIRMWARE_TYPES[0]:
                    with tarfile.TarFile(temporary_path, 'w') as tar:
                        tar.addfile(info, io.BytesIO(file_content))
                else:
                    with tarfile.TarFile(temporary_path, 'a') as tar:
                        tar.addfile(info, io.BytesIO(file_content))
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, self.rollback_fw_tar)
            temporary_path = None
            digest = hashlib.sha256()
            with open(self.rollback_fw_tar, "rb") as backup_file:
                for chunk in iter(lambda: backup_file.read(1024 * 1024), b""):
                    digest.update(chunk)
            metadata = {
                "path": self.rollback_fw_tar,
                "size": os.path.getsize(self.rollback_fw_tar),
                "sha256": digest.hexdigest(),
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "updater_version": __version__,
            }
            metadata_path = self.rollback_fw_tar + ".json"
            metadata_tmp = metadata_path + ".tmp"
            with open(metadata_tmp, "w", encoding="utf-8") as metadata_file:
                json.dump(metadata, metadata_file, separators=(",", ":"), sort_keys=True)
                metadata_file.flush()
                os.fsync(metadata_file.fileno())
            os.chmod(metadata_tmp, 0o600)
            os.replace(metadata_tmp, metadata_path)
            self.interactor.progress_bar(start=False)
        except (OSError, UpgradeError) as e:
            if temporary_path:
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass
            self.interactor.progress_bar(start=False)
            message = e.err if isinstance(e, UpgradeError) else str(e)
            raise UpgradeError(message, ErrorCode.BACKUP_FAILED.value)
        print("Firmware backup ended\n")

    def update(self):
        """Update the firmware to the specified flash"""
        print("===================================================")
        print("IOT2050 firmware update started - DO NOT INTERRUPT!")
        print("===================================================")

        try:
            # Perform signature verification before starting the actual flashing
            if self.verify_signature:
                print("Verifying firmware signatures...")
                # The primary firmware (uboot) is the one to be signed
                firmware_name_to_verify = self.tarball.get_file_name(self.tarball.FIRMWARE_TYPES[0])
                if firmware_name_to_verify:
                    self.tarball.verify_firmware_signature(firmware_name_to_verify)
                    print(f"Signature for {firmware_name_to_verify} verified successfully.")
                else:
                    raise UpgradeError("Could not determine primary firmware name for signature verification.",
                                       ErrorCode.INVALID_FIRMWARE.value)
                print("Firmware signature verification complete. Proceeding with update.")

            for firmware_type in self.firmwares:
                if firmware_type == self.tarball.FIRMWARE_TYPES[2]:
                    continue
                self.interactor.progress_bar(info="Updating {}".format(firmware_type))

                self.firmwares[firmware_type].write()

                self.firmwares[firmware_type].firmware.seek(0)
                content = self.firmwares[firmware_type].firmware.read()
                firmware_md5 = self.__get_md5_digest(content)

                content = self.firmwares[firmware_type].read()
                read_out_md5 = self.__get_md5_digest(content)
                self.interactor.progress_bar(start=False)

                if firmware_md5 != read_out_md5:
                    raise UpgradeError("Firmware digest verification failed")
        except UpgradeError as e:
            self.interactor.progress_bar(start=False)
            raise UpgradeError(e.err, e.code)

    def __get_md5_digest(self, content):
        """Verify the update integrity"""
        md5 = hashlib.md5()

        md5.update(content)

        return md5.hexdigest()

class FirmwareTarball(object):
    """A FirmwareTarball models a upgrade package in specified format"""

    CONF_JSON = 'update.conf.json'
    UBOOT_ENV_FILE = 'u-boot-initial-env'
    FIRMWARE_SIG_EXT = '.sig'
    PUBLIC_KEY_PATH = '/usr/share/iot2050/fwu/public.key'

    # "env" must be after "uboot" because uboot update will overwrite env
    # partition
    FIRMWARE_TYPES = [
        "uboot",
        "env",
        "conf"
    ]

    # These limits prevent a small uploaded archive from expanding until it
    # exhausts the root filesystem. The largest firmware image is 16 MiB, so
    # 64 MiB leaves headroom while still bounding the extraction.
    MAX_MEMBERS = 128
    MAX_EXTRACTED_SIZE = 64 * 1024 * 1024

    def __init__(self, firmware_tarball, interactor, env_list,
                 verify_signature_flag=False, pg2_only=False):
        self.interactor = interactor
        self.firmware_tarball = firmware_tarball
        self.env_list = env_list
        self.verify_signature_flag = verify_signature_flag
        self.pg2_only = pg2_only

        # A private per-package directory makes the verified files immutable to
        # unprivileged users for the lifetime of the update operation.
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="iot2050-firmware-update-"
        )
        self.extract_path = self._temporary_directory.name
        self.firmware_tarball.seek(0)
        self.extracted_files = []
        try:
            self.__extract_safely()
        except (tarfile.TarError, EOFError, OSError) as error:
            self.close()
            raise UpgradeError(
                "Cannot read firmware update package",
                ErrorCode.INVALID_FIRMWARE.value,
            ) from error
        except Exception:
            self.close()
            raise

        self._board_info = BoardInfo()
        print("Current board: {}".format(self._board_info.board_name))

        # Parse the update configuration from the json file within the tarball
        # Deserialize the json file to an object so that we can use dot operator
        # to access the fields.
        try:
            self._jsonobj = json.load(
                self.get_file(self.CONF_JSON),
                object_hook=lambda d: Namespace(**d)
            )
        except ValueError:
            raise UpgradeError("Decoding JSON has failed")

        self.firmware_names = dict.fromkeys(self.FIRMWARE_TYPES)

    def __extract_safely(self):
        """Extract regular files without trusting tar paths or link metadata."""
        total_size = 0
        with tarfile.open(fileobj=self.firmware_tarball) as archive:
            members = archive.getmembers()
            if len(members) > self.MAX_MEMBERS:
                raise UpgradeError(
                    "Firmware package contains too many files",
                    ErrorCode.INVALID_FIRMWARE.value,
                )
            for member in members:
                normalized_name = member.name.removeprefix("./")
                # Update packages are intentionally flat. Rejecting all other
                # entry types also excludes symlinks, hardlinks and devices.
                if not member.isfile() or normalized_name != os.path.basename(normalized_name):
                    raise UpgradeError(
                        f"Unsafe firmware package member: {member.name}",
                        ErrorCode.INVALID_FIRMWARE.value,
                    )
                if normalized_name in ("", ".", "..") or "\0" in normalized_name:
                    raise UpgradeError(
                        "Invalid firmware package member name",
                        ErrorCode.INVALID_FIRMWARE.value,
                    )
                total_size += member.size
                if total_size > self.MAX_EXTRACTED_SIZE:
                    raise UpgradeError(
                        "Firmware package expands beyond the size limit",
                        ErrorCode.INVALID_FIRMWARE.value,
                    )
                source = archive.extractfile(member)
                if source is None:
                    raise UpgradeError(
                        f"Cannot read firmware package member: {member.name}",
                        ErrorCode.INVALID_FIRMWARE.value,
                    )
                destination = os.path.join(self.extract_path, normalized_name)
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                if hasattr(os, "O_NOFOLLOW"):
                    flags |= os.O_NOFOLLOW
                destination_fd = os.open(destination, flags, 0o600)
                try:
                    with source, os.fdopen(destination_fd, "wb") as output:
                        shutil.copyfileobj(source, output)
                except Exception:
                    try:
                        os.close(destination_fd)
                    except OSError:
                        pass
                    raise
                self.extracted_files.append(destination)

    def close(self):
        temporary_directory = getattr(self, "_temporary_directory", None)
        if temporary_directory is not None:
            temporary_directory.cleanup()
            self._temporary_directory = None
        self.extracted_files = []

    def __del__(self):
        self.close()

    def __check_os(self, target_os, os_info) -> bool:
        for tos in target_os:
            try:
                current_version = version.parse(os_info[tos.key])
                required_version = version.parse(tos.min_version)
                if current_version >= required_version:
                    return True
            except version.InvalidVersion:
                if tos.key in os_info and os_info[tos.key] >= (tos.min_version):
                    return True
            print("\nFirmware requires a minimal version of ",
                  tos.min_version, ", the current OS has ",
                  os_info[tos.key], ".", sep="")

        return False

    def check_firmware(self):
        """Check if the tarball is a valid upgrade package"""
        if len(self.get_file_name(self.FIRMWARE_TYPES[0])) <= 0:
            return False
        return True

    def inspect(self):
        """Return the selected package metadata without touching the flash."""
        firmware_name = self.get_file_name(self.FIRMWARE_TYPES[0])
        if not firmware_name:
            raise UpgradeError(
                self.compatibility_error(),
                ErrorCode.INVALID_FIRMWARE.value,
            )
        if not os.path.isfile(self.get_file_path(firmware_name)):
            raise UpgradeError(
                f"Firmware image '{firmware_name}' is missing from the package",
                ErrorCode.INVALID_FIRMWARE.value,
            )
        selected = next(
            firmware for firmware in self._jsonobj.firmware
            if firmware.name == firmware_name
        )
        firmware_path = self.get_file_path(firmware_name)
        digest = hashlib.sha256()
        with open(firmware_path, "rb") as firmware:
            for chunk in iter(lambda: firmware.read(1024 * 1024), b""):
                digest.update(chunk)
        return {
            "firmware_name": firmware_name,
            "target_version": getattr(selected, "version", None),
            "description": getattr(selected, "description", None),
            "target_board": self._board_info.board_name,
            "firmware_sha256": digest.hexdigest(),
            "signature_present": os.path.isfile(
                firmware_path + self.FIRMWARE_SIG_EXT
            ),
        }

    def compatibility_error(self):
        """Explain why no firmware entry can be selected for this device."""
        firmware_entries = getattr(self._jsonobj, "firmware", [])
        board_matches = [
            firmware for firmware in firmware_entries
            if self._board_info.board_name in getattr(firmware, "target_boards", [])
        ]
        if not board_matches:
            supported = sorted({
                board
                for firmware in firmware_entries
                for board in getattr(firmware, "target_boards", [])
            })
            if self.pg2_only and supported and all("PG1" in board and "PG2" not in board
                                 for board in supported):
                return (
                    "This package contains PG1 firmware only; this updater "
                    "supports PG2 firmware only"
                )
            return (
                f"Firmware package does not target this board '{self._board_info.board_name}'. "
                f"Supported boards: {', '.join(supported) or 'none'}"
            )
        return (
            f"Firmware package contains no compatible image for board "
            f"'{self._board_info.board_name}' and OS version "
            f"'{self._board_info.os_info.get('VERSION_ID', 'unknown')}'"
        )

    def get_file_name(self, firmware_type):
        """Get the file names of working firmware"""
        res = []
        if self.FIRMWARE_TYPES[1] == firmware_type:
            res = self.UBOOT_ENV_FILE
            return res
        if self.FIRMWARE_TYPES[2] == firmware_type:
            res = self.CONF_JSON
            return res
        if not self.firmware_names[firmware_type]:
            for firmware in self._jsonobj.firmware:
                # This product image only supports the PG2 boot chain. PG1
                # entries may remain in a shared update archive, but must not
                # become selectable candidates for this updater.
                target_boards = getattr(firmware, "target_boards", [])
                if self.pg2_only and not any(
                    "PG2" in board or "Advanced SM" in board
                    for board in target_boards):
                    continue
                if self._board_info.board_name in firmware.target_boards:
                    # Be forward compatible, the previous uboot firmware
                    # tarballs don't have the type node
                    if not hasattr(firmware, "type"):
                        firmware.type = self.FIRMWARE_TYPES[0]

                    if firmware.type ==  firmware_type:
                        target_os = []
                        try:
                            target_os = self._jsonobj.target_os
                        except AttributeError:
                            pass

                        # local target_os configuration prior to global
                        try:
                            target_os = firmware.target_os
                        except AttributeError:
                            pass

                        # Get available firmware names by checking the board name
                        # and the os information, or the firmware w/o target_os node
                        # which means it doesn't care the OS info.
                        if len(target_os) == 0 or \
                                self.__check_os(target_os, self._board_info.os_info):
                            res.append(firmware.name)

            if len(res) > 1:
                # Ask user to pick one firmware image to update
                print("Please select which firmware image to update:")
                for n in res:
                    print("{}\t{}".format(res.index(n) + 1, n))

                choice = int(self.interactor.interact("-> "))
                while choice > len(res) or choice < 1:
                    print("Out of range, please reinput your choice:")
                    choice = int(self.interactor.interact("-> "))

                res = res[choice - 1]

            self.firmware_names[firmware_type] = "".join(res)

        return self.firmware_names[firmware_type]

    def get_file(self, name):
        """Get the file object of specified name"""
        file = os.path.join(self.extract_path, name)
        try:
            return open(file, 'rb')
        except OSError as error:
            raise UpgradeError(
                f"Firmware package file is unavailable: {name}",
                ErrorCode.INVALID_FIRMWARE.value,
            ) from error

    def get_file_path(self, name):
        """Get the file object of specified name"""
        file = os.path.join(self.extract_path, name)

        return file

    def __get_suggest_preserved_uboot_env(self):
        """Get the default uboot env list from tarball"""
        try:
            return self._jsonobj.suggest_preserved_uboot_env
        except Exception:
            raise UpgradeError("Get suggested preserved uboot env failed")

    def get_preserved_uboot_env(self):
        try:
            if self.env_list:
                if isinstance(self.env_list, (list, tuple)):
                    preserved_uboot_env_name = self.env_list
                elif isinstance(self.env_list, str):
                    preserved_uboot_env_name = self.env_list.split(',')
                else:
                    raise UpgradeError(
                        "Invalid preserved U-Boot environment list",
                        ErrorCode.INVALID_FIRMWARE.value,
                    )
            else:
                preserved_uboot_env_name = \
                   self.__get_suggest_preserved_uboot_env()
                if not isinstance(preserved_uboot_env_name, (list, tuple)):
                    raise UpgradeError(
                        "Invalid preserved U-Boot environment list",
                        ErrorCode.INVALID_FIRMWARE.value,
                    )

            if not preserved_uboot_env_name:
                return []

            preserved_uboot_env_value = []
            for env_name in preserved_uboot_env_name:
                if not isinstance(env_name, str) or not env_name.strip():
                    raise UpgradeError(
                        "Invalid preserved U-Boot environment name",
                        ErrorCode.INVALID_FIRMWARE.value,
                    )
                try:
                    env_value = subprocess.run(
                        ["fw_printenv", env_name.strip()],
                        stdout=subprocess.PIPE, text=True, check=True,
                        timeout=10).stdout.strip()
                except (OSError, subprocess.CalledProcessError,
                        subprocess.TimeoutExpired) as error:
                    raise UpgradeError(
                        "Failed to read preserved U-Boot environment",
                        ErrorCode.FAILED.value,
                    ) from error
                if not env_value:
                    raise UpgradeError(
                        "Failed to read preserved U-Boot environment",
                        ErrorCode.FAILED.value,
                    )
                preserved_uboot_env_value.append(env_value)

            return preserved_uboot_env_value
        except UpgradeError as e:
            raise UpgradeError(e.err, e.code) from e

    def __remove_line_by_index(self, file, index):
        with open(file, 'r+') as fp:
            lines = fp.readlines()
            fp.seek(0)
            fp.truncate()
            for number, line in enumerate(lines):
                if number != index:
                    fp.write(line)

    def __remove_duplicate_default_env(self, uboot_env_file, env_list):
        with open(uboot_env_file, 'r', encoding='utf-8') as f:
            default_env_list = [i.split('=')[0] for i in f.readlines()]
        for value in env_list:
            if value.split('=')[0] in default_env_list:
                value_index = default_env_list.index(value.split('=')[0])
                self.__remove_line_by_index(uboot_env_file, value_index)

    def generate_env_firmware(self, env_list):
        """Generate the update env file based on env_list"""
        uboot_default_env_file = os.path.join(
            self.extract_path, self.UBOOT_ENV_FILE)
        uboot_env_assemble_file = os.path.join(
            self.extract_path, "env_assemble_file")
        assert os.path.isfile(uboot_default_env_file)
        # assemble the env
        shutil.copy(uboot_default_env_file, uboot_env_assemble_file)
        self.__remove_duplicate_default_env(uboot_env_assemble_file, env_list)

        with open(uboot_env_assemble_file, encoding="utf-8", mode="a") as file:
            for value in env_list:
                file.write(value)
                file.write("\n")

        return uboot_env_assemble_file, open(uboot_env_assemble_file, 'rb')

    def verify_firmware_signature(self, firmware_name):
        """
        Verifies the digital signature of a firmware file.
        Expects a signature file with the same name as the firmware
        but with a .sig extension in the tarball.
        The public key is expected at PUBLIC_KEY_PATH.
        """
        firmware_path = self.get_file_path(firmware_name)
        signature_path = firmware_path + self.FIRMWARE_SIG_EXT

        if not os.path.exists(firmware_path):
            raise UpgradeError(f"Firmware file not found: {firmware_path}",
                               ErrorCode.INVALID_FIRMWARE.value)
        if not os.path.exists(signature_path):
            # If --verify is used, signature file is mandatory
            if self.verify_signature_flag:
                raise UpgradeError(f"Signature file not found {signature_path}. Signature verification is enabled, but the .sig file is missing.",
                                   ErrorCode.MISSING_SIGNATURE.value)
            else:
                # This case should ideally not be reached if verify_signature_flag is false
                # as this method would only be called if verify_signature_flag is true.
                # However, as a safeguard:
                print(f"Warning: Signature file not found for {firmware_name}. Skipping signature verification.")
                return

        if not os.path.exists(self.PUBLIC_KEY_PATH):
            raise UpgradeError(f"Public key not found at {self.PUBLIC_KEY_PATH}. Cannot verify signature.",
                               ErrorCode.MISSING_PUBLIC_KEY.value)

        try:
            with open(self.PUBLIC_KEY_PATH, "rb") as f:
                pubkey = serialization.load_pem_public_key(f.read())

            with open(firmware_path, "rb") as f:
                message = f.read()

            with open(signature_path, "rb") as f:
                sig = f.read()

            pubkey.verify(sig, message, padding.PKCS1v15(), hashes.SHA512())
            print(f"Signature for {firmware_name} is GOOD.")
        except InvalidSignature:
            raise UpgradeError(f"BAD SIGNATURE for {firmware_name}. Firmware is malicious or corrupted. Aborting update.",
                               ErrorCode.BAD_SIGNATURE.value)
        except Exception as e:
            raise UpgradeError(f"Error during signature verification for {firmware_name}: {e}",
                               ErrorCode.FAILED.value)

class BoardInfo(object):
    """The BoardInfo represents the updating IOT2050 board information"""
    def __init__(self):
        self.board_name = self._get_board_name()
        self.os_info = self._get_os_info()

    def _get_board_name(self) -> str:
        """
        Get the board name by checking the device tree node
        /proc/device-tree/model
        """
        with open('/proc/device-tree/model') as f_model:
            board_name = f_model.read().strip('\0')

        return board_name

    def _get_os_info(self) -> dict:
        '''
        Get the OS information by parsing the /etc/os-release

        Returned is a dict that converted from /etc/os-release, for example:
            NAME="debian"
            VERSION_ID="3.1.1"

        =>
            {
                "NAME": "debian"
                "VERSION_ID": "3.1.1"
            }
        '''
        with open('/etc/os-release') as f:
            return {
                l.split('=')[0]:
                l.strip().split('=')[-1].strip('"')
                for l in f.readlines()
            }

class NonInteractiveInterface(object):
    """Progress adapter for trusted callers such as the local manager."""

    def __init__(self, progress=None):
        self.progress = progress or (lambda phase: None)

    def interact(self, *args):
        raise UpgradeError(
            "Interactive input is not allowed for managed updates",
            ErrorCode.FAILED.value,
        )

    def print_info(self, *args):
        pass

    def progress_bar(self, info="", interval=0.2, start=True):
        if start and info:
            self.progress(info.lower().replace(" ", "-"))


def inspect_system_firmware(firmware_path, public_key_path=None, pg2_only=False):
    """Validate compatibility and signature without accessing flash devices."""
    interactor = NonInteractiveInterface()
    with open(firmware_path, "rb") as archive:
        package = FirmwareTarball(archive, interactor, None, True, pg2_only)
        try:
            if public_key_path is not None:
                package.PUBLIC_KEY_PATH = public_key_path
            details = package.inspect()
            package.verify_firmware_signature(details["firmware_name"])
            details["signature_verified"] = True
            details["public_key"] = package.PUBLIC_KEY_PATH
            return details
        finally:
            package.close()


def update_system_firmware(firmware_path, backup_dir=None,
                           preserve_list=None, reset=False, progress=None,
                           public_key_path=None, pg2_only=False,
                           backup=True, verify_signature=True):
    """Perform a signed update without prompts or reboot.

    The rollback backup is created once; only the flash step is retried on
    transient write failures. Verification, signature and compatibility
    failures are deterministic and are not retried.
    """
    interactor = NonInteractiveInterface(progress)
    with open(firmware_path, "rb") as archive:
        package = FirmwareTarball(
            archive, interactor, preserve_list,
            verify_signature_flag=verify_signature,
            pg2_only=pg2_only
        )
        updater = None
        try:
            if public_key_path is not None:
                package.PUBLIC_KEY_PATH = public_key_path
            details = package.inspect()
            # Verify before FirmwareUpdate gathers environment state or opens
            # flash devices. FirmwareUpdate verifies again immediately before
            # writing, using the same private extracted files.
            if verify_signature:
                package.verify_firmware_signature(details["firmware_name"])
            updater = FirmwareUpdate(
                package, backup_dir, interactor,
                rollback=False, reset=reset,
                verify_signature=verify_signature,
            )
            if backup:
                progress and progress("preparing-backup")
                updater.backup()
            progress and progress("flashing-system")
            last_error = None
            for attempt in range(4):
                try:
                    updater.update()
                    last_error = None
                    break
                except UpgradeError as error:
                    last_error = error
                    # Deterministic failures: retrying the flash step cannot
                    # help, so surface them immediately.
                    if error.code in (
                            ErrorCode.INVALID_FIRMWARE.value,
                            ErrorCode.MISSING_SIGNATURE.value,
                            ErrorCode.MISSING_PUBLIC_KEY.value,
                            ErrorCode.BAD_SIGNATURE.value):
                        raise
                    if attempt < 3:
                        print(f"{error.err}, trying again!")
                        progress and progress("retrying-flash")
            if last_error is not None:
                raise last_error
            return {
                **details,
                "signature_verified": verify_signature,
                "backup_path": updater.rollback_fw_tar if backup else None,
                "reboot_required": True,
            }
        finally:
            if updater is not None:
                updater.close()
            package.close()


def force_update_system_firmware(firmware_path, progress=None):
    """Perform a raw U-Boot update without a package backup."""
    interactor = NonInteractiveInterface(progress)
    with open(firmware_path, "rb") as firmware:
        updater = ForceUpdate(interactor, firmware)
        progress and progress("flashing-system")
        updater.update()
    return {
        "mode": "force",
        "reboot_required": True,
    }


def serve_system_firmware_grpc():
    """Serve System Firmware operations from this single backend module."""
    import grpc
    from iot2050_system_firmware_pb2 import (
        CapabilitiesReply,
        Empty,
        InspectionReply,
        OperationRequest,
        OperationReply,
        RollbackReply,
    )
    from iot2050_system_firmware_pb2_grpc import (
        SystemFirmwareServicer,
        add_SystemFirmwareServicer_to_server,
    )
    from iot2050_firmware_operation_store import FirmwareOperationStore

    socket_path = SYSTEM_FIRMWARE_SOCKET_PATH
    firmware_dir = DEFAULT_FIRMWARE_DIR
    firmware_pattern = DEFAULT_FIRMWARE_PATTERN
    max_firmware_size = DEFAULT_MAX_FIRMWARE_SIZE

    class Service(SystemFirmwareServicer):
        def __init__(self):
            self.operation_store = FirmwareOperationStore(
                "/var/lib/iot2050/system-firmware/operations"
            )
            self.operation_store.recover_running()
            self.operations_executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=1
            )

        @staticmethod
        def _json(value):
            return json.dumps(value or {}, separators=(",", ":"), default=str)

        # Semantic error codes returned to gRPC clients. The numeric
        # ErrorCode values are kept as the CLI exit-code contract.
        ERROR_CODES = {
            3: "backup-failed",
            4: "rollback-failed",
            5: "flashing-failed",
            7: "firmware-incompatible",
            9: "missing-signature",
            10: "missing-key",
            11: "bad-signature",
        }

        @classmethod
        def _message(cls, error):
            messages = {
                3: "System firmware backup failed",
                4: "System firmware rollback failed",
                5: "System firmware flashing or readback failed",
                7: "The firmware package is not compatible with this device",
                9: "The firmware signature is missing",
                10: "The firmware verification key is unavailable",
                11: "The firmware signature is invalid",
            }
            return messages.get(
                getattr(error, "code", None),
                "System firmware operation failed",
            )

        @classmethod
        def _failure(cls, error):
            code = cls.ERROR_CODES.get(
                getattr(error, "code", None), "operation-failed")
            return {
                "ok": False,
                "code": code,
                "message": cls._message(error),
                "details_json": "",
            }

        @staticmethod
        def _firmware_path(requested):
            path = requested
            if not path:
                candidates = sorted(
                    item for item in glob.glob(
                        os.path.join(firmware_dir, firmware_pattern)
                    )
                    if os.path.isfile(item) and not os.path.islink(item)
                )
                path = candidates[-1] if candidates else None
            if path is None:
                raise ValueError("The system firmware package is unavailable")
            if os.path.islink(path) or not os.path.isfile(path):
                raise ValueError(
                    "The system firmware package must be a regular file")
            if os.path.getsize(path) > max_firmware_size:
                raise ValueError("The system firmware package is too large")
            return path

        @staticmethod
        def _response(response):
            return response

        def _submit(self, function):
            if self.operation_store.has_running():
                return OperationReply(
                    ok=False,
                    code="firmware-busy",
                    message="System firmware operation is already running",
                    state="unknown",
                )
            operation_id = str(uuid.uuid4())
            self.operation_store.create(operation_id, {
                "state": "running",
                "ok": False,
                "code": "operation-running",
                "message": "System firmware operation is running",
                "stage": "starting",
                "details_json": "",
            })

            def progress(stage):
                try:
                    self.operation_store.update(operation_id, stage=stage)
                except (OSError, KeyError):
                    pass

            def run():
                try:
                    details = function(progress)
                    outcome = {
                        "state": "succeeded",
                        "ok": True,
                        "code": "ok",
                        "message": "System firmware operation completed",
                        "stage": "completed",
                        "details_json": self._json(details),
                    }
                except Exception as error:
                    outcome = self._failure(error)
                    outcome["state"] = "failed"
                self.operation_store.update(operation_id, **outcome)

            self.operations_executor.submit(run)
            return OperationReply(
                ok=True,
                code="operation-started",
                message="System firmware operation started",
                operation_id=operation_id,
                state="running",
                stage="starting",
            )

        def _operation(self, operation_id):
            try:
                operation = self.operation_store.read(operation_id)
            except KeyError:
                return OperationReply(
                    ok=False,
                    code="operation-not-found",
                    message="System firmware operation was not found",
                    state="unknown",
                )
            return OperationReply(
                ok=operation["ok"],
                code=operation["code"],
                message=operation["message"],
                details_json=operation["details_json"],
                operation_id=operation_id,
                state=operation["state"],
                stage=operation.get("stage", ""),
            )

        def _perform_update(self, request, progress=None):
            firmware_path = self._firmware_path(request.firmware_path)
            backup_dir = validate_backup_dir(
                request.backup_dir,
                allow_custom=request.legacy_cli,
            )
            if request.force:
                return force_update_system_firmware(firmware_path,
                                                    progress=progress)
            return update_system_firmware(
                firmware_path,
                backup_dir,
                preserve_list=list(request.preserve_list) or None,
                reset=request.reset,
                pg2_only=request.pg2_only,
                backup=not request.no_backup,
                verify_signature=(
                    request.verify_signature if request.legacy_cli else True
                ),
                progress=progress,
            )

        def _perform_rollback(self, request, progress=None):
            backup_dir = validate_backup_dir(
                request.backup_dir,
                allow_custom=request.legacy_cli,
            )
            return rollback_system_firmware(backup_dir, progress=progress)

        def GetCapabilities(self, request: Empty, context):
            return CapabilitiesReply(
                supported=True,
                details_json=self._json({
                    "backend": "system",
                    "operations": ["inspect", "update", "rollback"],
                    "backup": DEFAULT_ROLLBACK_DIR,
                    "requires_signature": True,
                }),
            )

        def Inspect(self, request, context):
            try:
                details = inspect_system_firmware(
                    self._firmware_path(request.firmware_path),
                    pg2_only=request.pg2_only,
                )
                return InspectionReply(
                    ok=True,
                    code="ok",
                    message="System firmware inspection completed",
                    details_json=self._json(details),
                )
            except Exception as error:
                return InspectionReply(**self._failure(error))

        def Update(self, request, context):
            try:
                details = self._perform_update(request)
                return OperationReply(
                    ok=True,
                    code="ok",
                    message="System firmware update completed",
                    details_json=self._json(details),
                )
            except Exception as error:
                return OperationReply(**self._failure(error))

        def StartUpdate(self, request, context):
            return self._submit(
                lambda progress: self._perform_update(request, progress))

        def GetOperation(self, request: OperationRequest, context):
            return self._operation(request.operation_id)

        def InspectRollback(self, request, context):
            try:
                backup_dir = validate_backup_dir(
                    request.backup_dir,
                    allow_custom=request.legacy_cli,
                )
                details = inspect_system_rollback(backup_dir)
                return RollbackReply(
                    ok=True,
                    code="ok",
                    message="System firmware rollback inspection completed",
                    details_json=self._json(details),
                )
            except Exception as error:
                return RollbackReply(**self._failure(error))

        def Rollback(self, request, context):
            try:
                details = self._perform_rollback(request)
                return OperationReply(
                    ok=True,
                    code="ok",
                    message="System firmware rollback completed",
                    details_json=self._json(details),
                )
            except Exception as error:
                return OperationReply(**self._failure(error))

        def StartRollback(self, request, context):
            return self._submit(
                lambda progress: self._perform_rollback(request, progress))

    socket_file = Path(socket_path)
    socket_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        socket_file.unlink()
    except FileNotFoundError:
        pass

    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=1),
        options=(
            ("grpc.max_receive_message_length", max_firmware_size),
            ("grpc.max_send_message_length", max_firmware_size),
        ),
    )
    service = Service()
    add_SystemFirmwareServicer_to_server(service, server)
    if server.add_insecure_port(f"unix://{socket_path}") == 0:
        raise RuntimeError("Unable to bind the System Firmware gRPC socket")
    old_umask = os.umask(0o177)
    try:
        server.start()
        os.chmod(socket_file, 0o600)
    finally:
        os.umask(old_umask)
    try:
        server.wait_for_termination()
    finally:
        service.operations_executor.shutdown(wait=False, cancel_futures=True)
        server.stop(grace=0)
        try:
            socket_file.unlink()
        except FileNotFoundError:
            pass


def inspect_system_rollback(backup_dir=None):
    """Inspect the shared local rollback artifact without touching flash."""
    rollback_path = resolve_rollback_path(backup_dir)
    if not os.path.isfile(rollback_path) or not tarfile.is_tarfile(rollback_path):
        raise UpgradeError(
            "No rollback firmware exists", ErrorCode.ROLLBACK_FAILED.value)
    metadata_path = rollback_path + ".json"
    try:
        with open(metadata_path, encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        digest = hashlib.sha256()
        with open(rollback_path, "rb") as backup_file:
            for chunk in iter(lambda: backup_file.read(1024 * 1024), b""):
                digest.update(chunk)
        if metadata.get("size") != os.path.getsize(rollback_path) or \
           metadata.get("sha256") != digest.hexdigest():
            raise UpgradeError(
                "Rollback backup integrity check failed",
                ErrorCode.ROLLBACK_FAILED.value,
            )
    except (OSError, ValueError, KeyError) as error:
        raise UpgradeError(
            "Rollback backup metadata is unavailable",
            ErrorCode.ROLLBACK_FAILED.value,
        ) from error
    return {
        "available": True,
        "size": metadata["size"],
        "sha256": metadata["sha256"],
        "created_at": metadata.get("created_at"),
        "updater_version": metadata.get("updater_version"),
        "source": "shared-local-backup",
    }


def rollback_system_firmware(backup_dir=None, progress=None):
    """Perform one non-interactive rollback using the shared local backup."""
    progress and progress("preparing-rollback")
    details = inspect_system_rollback(backup_dir)
    interactor = NonInteractiveInterface(progress)
    rollback_root = backup_dir
    updater = None
    try:
        updater = FirmwareUpdate(
            None, rollback_root, interactor, rollback=True,
            verify_signature=False,
        )
        progress and progress("flashing-system")
        updater.update()
        return {
            **details,
            "mode": "rollback",
            "reboot_required": True,
        }
    except UpgradeError as error:
        if error.code == ErrorCode.ROLLBACK_FAILED.value:
            raise
        raise UpgradeError(error.err, ErrorCode.ROLLBACK_FAILED.value) \
            from error
    except Exception as error:
        raise UpgradeError(str(error), ErrorCode.ROLLBACK_FAILED.value) \
            from error
    finally:
        if updater is not None:
            updater.close()


def main(argv):
    """The main function"""

    if argv and len(argv) == 2 and argv[1] == "--grpc-server":
        serve_system_firmware_grpc()
        return ErrorCode.SUCCESS.value

    print("This module is a gRPC service. Use the iot2050-firmware-update "
          "CLI or the System Firmware gRPC service.", file=sys.stderr)
    return 2

if __name__ == '__main__':
    CODE = main(sys.argv)
    sys.exit(CODE)