#!/usr/bin/env python3
import sys
import os
import fcntl
import struct
import mmap
import hashlib
from optparse import OptionParser

force_update = False


def FirmwareUpdateException(str):
    """Report the error info and exit"""
    if not force_update:
        print(str)
        sys.exit(1)


class FirmwareUpdate(object):
    def __init__(self, force):
        self.force_update = force

    def sha256_check(self, file):
        """Firmware Sha256 Check"""
        check_sha256_file = file+'.sha256'
        file_sha256 = None
        try:
            with open(check_sha256_file, 'r') as f:
                file_sha256 = str(f.read()).split()[0]
        except FileNotFoundError:
            FirmwareUpdateException("sha256 file not exists")

        try:
            with open(file, 'rb+') as f:
                method = hashlib.sha256()
                method.update(f.read())
                hash_code = method.hexdigest()
        except FileNotFoundError:
            print("%s not Exists" % file)
            sys.exit(1)

        if file_sha256 != hash_code:
            if(self.force_update is not True):
                FirmwareUpdateException("Image Checksum is not Correct")

    def get_path_type_value(self, path):
        """get the path value"""
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print("%s is not exists" % path)
            sys.exit(1)

    @staticmethod
    def flash_erase(dev, start, nbytes):
        """This function erase the flash

        @dev:the flash device

        @start:start address

        @nbytes:the number of erase bytes
        """
        MEMERASE = 0x40084d02

        try:
            fd = os.open(dev, os.O_SYNC | os.O_RDWR)
        except FileNotFoundError:
            print("failed to open %s" % dev)
            sys.exit(1)

        ioctl_data = struct.pack('II', start, nbytes)

        try:
            fcntl.ioctl(fd, MEMERASE, ioctl_data)
        except IOError:
            print("ioctl failed")
            sys.exit(1)

        os.close(fd)

    def cpu_id_check(self):
        """cpu id check"""
        cpu_device_id = [0x142ba, 0x142fa, 0x140ff]
        cpuid_register_addr = 0x43000018
        base_addr = cpuid_register_addr & ~(mmap.PAGESIZE - 1)
        base_addr_offset = cpuid_register_addr - base_addr
        try:
            f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
        except FileNotFoundError:
            print("Open /dev/mem Failed")
            sys.exit(1)

        mem = mmap.mmap(f, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ, offset=base_addr)
        mem.seek(base_addr_offset)
        data = []
        data.append(struct.unpack('I', mem.read(4))[0])
        device_id = hex(data[0])
        current_id = int(device_id, 16) >> 11
        if current_id not in cpu_device_id:
            FirmwareUpdateException("Upgrade is not supported for the board")

    def update_firmware(self, filename):
        """Update Firmware"""
        mtd_num = 0
        img_pos = 0

        print("===================================================")
        print("IOT2050 firmware update started - DO NOT INTERRUPT!")
        print("===================================================")

        while True:
            mtd_sys_path = "/sys/bus/platform/devices/47040000.spi/mtd/mtd{}".format(mtd_num)
            mtd_name_path = "{}/name".format(mtd_sys_path)
            mtd_size_path = "{}/size".format(mtd_sys_path)
            mtd_erasesize_path = "{}/erasesize".format(mtd_sys_path)
            mtd_dev_path = "/dev/mtd{}".format(mtd_num)

            mtd_size = self.get_path_type_value(mtd_size_path)
            mtd_size = int(mtd_size)

            mtd_erasesize = self.get_path_type_value(mtd_erasesize_path)
            mtd_erasesize = int(mtd_erasesize)

            mtd_name = self.get_path_type_value(mtd_name_path)

            print("Updating %-20s" % mtd_name.strip(),end="")
            if mtd_name.strip() == "ospi.rootfs":
                print("\n\nCompleted. Please reboot the device\n")
                sys.exit(0)

            mtd_pos = 0
            while mtd_pos < mtd_size:
                try:
                    with open(mtd_dev_path, 'rb') as mtd:
                        mtd.seek(mtd_pos)
                        mtd_contents = mtd.read(mtd_erasesize)
                except FileNotFoundError:
                    print("Open %s failed" % mtd_dev_path)
                    sys.exit(1)

                with open(filename, 'rb') as firmware:
                    firmware.seek(img_pos)
                    firmware_contents = firmware.read(mtd_erasesize)

                if not mtd_contents == firmware_contents:
                    print("U", end="")
                    sys.stdout.flush()
                    self.flash_erase(mtd_dev_path, mtd_pos, mtd_erasesize)
                    with open(mtd_dev_path, 'wb') as mtd_unity:
                        mtd_unity.seek(mtd_pos)
                        mtd_unity.write(firmware_contents)
                else:
                    print(".", end="")
                    sys.stdout.flush()
                mtd_pos = mtd_pos+mtd_erasesize
                img_pos = img_pos+mtd_erasesize
            print()
            mtd_num = (mtd_num+1)


def main(argv):
    usage = "%prog [Options] Firmware"
    parser = OptionParser(usage)
    parser.add_option('-f', '--force', action='store_true', dest='force', default=False, help="Force update, ignoring image checksum or device ID mismatches")

    (options, args) = parser.parse_args()

    if not args:
        print(parser.parse_args(['-h']))
        sys.exit(1)

    erase_env_input = input("\nWarning: All U-Boot environment variables will be reset to factory settings. Continue (y/N)? ")

    if not erase_env_input == "y":
        sys.exit(1)

    if options.force:
        force_update_input = input("\nWarning: Enforced update may render device unbootable. Continue (y/N)? ")
        if not force_update_input == "y":
            sys.exit(1)
        else:
            global force_update
            force_update = options.force

    filename = argv[-1]

    firmupdate = FirmwareUpdate(options.force)

    firmupdate.sha256_check(filename)

    firmupdate.cpu_id_check()

    firmupdate.update_firmware(filename)


if __name__ == '__main__':
    main(sys.argv)
