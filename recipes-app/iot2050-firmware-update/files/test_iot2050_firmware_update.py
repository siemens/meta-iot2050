import os
import fcntl
import subprocess
import unittest
from unittest.mock import patch, MagicMock, Mock, mock_open
from iot2050_firmware_update import (
        main,
        ErrorCode,
        FirmwareUpdate,
        FirmwareTarball,
        UserInterface,
        Firmware,
        MtdDevice,
        BootloaderFirmware,
        EnvFirmware,
        ForceUpdate,
        BoardInfo,
        UpgradeError,
)

class TestUpgradeError(unittest.TestCase):
    def test_error_with_default_code(self):
        error = UpgradeError("Test error")
        self.assertEqual(error.err, "Test error")
        self.assertEqual(error.code, ErrorCode.FAILED.value)

    def test_error_with_custom_code(self):
        error = UpgradeError("Test error", ErrorCode.SUCCESS.value)
        self.assertEqual(error.err, "Test error")
        self.assertEqual(error.code, ErrorCode.SUCCESS.value)

    def test_error_string_representation(self):
        error = UpgradeError("Test error", ErrorCode.SUCCESS.value)
        self.assertEqual(str(error), "Test error")


class TestFirmware(unittest.TestCase):
    class FirmwareSubclass(Firmware):
        def write(self):
            pass

        def read(self):
            pass

    @patch('builtins.open', new_callable=Mock)
    def test_init_with_file(self, mock_open):
        firmware_file = "firmware.bin"
        firmware = self.FirmwareSubclass(open(firmware_file, "rb"))
        self.assertEqual(firmware.firmware, mock_open.return_value)

    @patch('builtins.open', new_callable=Mock)
    def test_del(self, mock_open):
        firmware_file = "firmware.bin"
        firmware = self.FirmwareSubclass(open(firmware_file, "rb"))
        firmware_id = id(firmware)
        del firmware
        self.assertRaises(Exception, lambda: id(firmware))
        mock_open.return_value.close.assert_called_once()

    @patch('builtins.open', new_callable=Mock)
    def test_init_with_invalid_file(self, mock_open):
        with self.assertRaises(UpgradeError):
            self.FirmwareSubclass("invalid_file")


class TestMtdDevice(unittest.TestCase):
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open, read_data="123")
    def test_get_mtd_info(self, mock_file, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ['0']
        mtd = MtdDevice()
        mtd_dev_path, mtd_size, mtd_erasesize, mtd_name = mtd.get_mtd_info(0)
        self.assertEqual(mtd_dev_path, "/dev/mtd0")
        self.assertEqual(mtd_size, 123)
        self.assertEqual(mtd_erasesize, 123)
        self.assertEqual(mtd_name, "123")

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open, read_data="123")
    def test_get_mtd_info_upgrade_error(self, mock_file, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ['0']
        mock_file.side_effect = UpgradeError("Failed to open file")

        mtd = MtdDevice()
        mtd_num = 0

        with self.assertRaises(UpgradeError) as context:
            mtd.get_mtd_info(0)

        self.assertTrue("Failed to open file" in str(context.exception))

    @patch('os.close')
    @patch('os.read', return_value=b'test data')
    @patch('os.open', return_value=123)
    def test_read(self, mock_os_open, mock_os_read, mock_os_close):
        mtd = MtdDevice()
        mtd_dev_path = "/dev/mtd0"
        mtd_size = 123
        mtd_erasesize = 123
        file_size = 123

        result = mtd.read(mtd_dev_path, mtd_size, mtd_erasesize, file_size)

        mock_os_open.assert_called_once_with(mtd_dev_path, os.O_SYNC | os.O_RDONLY)
        self.assertEqual(mock_os_read.call_count, 1)
        mock_os_close.assert_called_once_with(123)
        self.assertEqual(result, b'test data')

    @patch('os.open', side_effect=IOError("Test error"))
    def test_read_open_fails(self, mock_os_open):
        mtd = MtdDevice()
        mtd_dev_path = "/dev/mtd0"
        mtd_size = 123
        mtd_erasesize = 123
        file_size = 123

        with self.assertRaises(UpgradeError) as context:
            mtd.read(mtd_dev_path, mtd_size, mtd_erasesize, file_size)

        self.assertTrue("Opening {} failed".format(mtd_dev_path) in str(context.exception))

    @patch('fcntl.ioctl', return_value=None)
    @patch('os.close')
    @patch('os.write', return_value=None)
    @patch('os.lseek', return_value=None)
    @patch('os.read', return_value=b'\xff' * 123)
    @patch('os.open', return_value=123)
    def test_write(self, mock_os_open, mock_os_read, mock_os_lseek, mock_os_write, mock_os_close, mock_ioctl):
        mtd = MtdDevice()
        mtd_dev_path = "/dev/mtd0"
        mtd_size = 123
        mtd_erasesize = 123
        file_obj = mock_open(read_data=b'test data').return_value
        file_size = 123

        result = mtd.write(mtd_dev_path, mtd_size, mtd_erasesize, file_obj, file_size)

        mock_os_open.assert_called_once_with(mtd_dev_path, os.O_SYNC | os.O_RDWR)
        self.assertEqual(mock_os_read.call_count, 1)
        self.assertEqual(mock_os_lseek.call_count, 1)
        self.assertEqual(mock_os_write.call_count, 1)
        mock_os_close.assert_called_once_with(123)
        self.assertEqual(result, 0)

    @patch('os.open', side_effect=IOError("Test error"))
    def test_write_open_fails(self, mock_os_open):
        mtd = MtdDevice()
        mtd_dev_path = "/dev/mtd0"
        mtd_size = 123
        mtd_erasesize = 123
        file_obj = mock_open(read_data=b'test data').return_value
        file_size = 123

        with self.assertRaises(UpgradeError) as context:
            mtd.write(mtd_dev_path, mtd_size, mtd_erasesize, file_obj, file_size)

        self.assertTrue("Opening {} failed".format(mtd_dev_path) in str(context.exception))


class TestBootloaderFirmware(unittest.TestCase):
    @patch('iot2050_firmware_update.MtdDevice')
    @patch('os.path.getsize')
    def setUp(self, mock_mtd_device, mock_os_path):
        self.firmware_file = MagicMock()
        self.firmware = BootloaderFirmware(self.firmware_file)
        self.mock_mtd_device = mock_mtd_device
        self.mock_os_path = mock_os_path
        self.mock_mtd_device.get_mtd_info.return_value = self.test_values()
        self.mock_os_path.getsize.return_value = 100
        self.mock_os_path.return_value = 100

def test_values(self):
    return "mtd_dev_path", 100, 100, "mtd_name"

    def test_write(self):
        self.mock_mtd_device.write.return_value = 0
        self.firmware.write()
        self.mock_mtd_device.write.assert_called()

    def test_write_with_upgrade_error(self):
        self.mock_mtd_device.write.side_effect = UpgradeError("Error")
        with self.assertRaises(UpgradeError):
            self.firmware.write()

    def test_read(self):
        self.mock_mtd_device.read.return_value = b"binary data"
        mtd_dev_path, mtd_size, mtd_erasesize, mtd_name = self.mock_mtd_device.get_mtd_info(0)
        print("Lee: ", "mtd_dev_path = ", mtd_dev_path, ", mtd_size = ", mtd_size, ", mtd_erasesize = ", mtd_erasesize, ", mtd_name = ", mtd_name)
        print("Lee: ", self.mock_mtd_device.get_mtd_info(0))
        result = self.firmware.read()
        self.assertEqual(result, b"binary data")
        self.mock_mtd_device.read.assert_called()

    def test_read_with_upgrade_error(self):
        self.mock_mtd_device.read.side_effect = UpgradeError("Error")
        with self.assertRaises(UpgradeError):
            self.firmware.read()


class TestEnvFirmware(unittest.TestCase):
    def setUp(self):
        self.mock_mtd_device = patch('iot2050_firmware_update.MtdDevice').start()
        self.mock_subprocess_run = patch('subprocess.run').start()
        self.mock_os_path_getsize = patch('os.path.getsize').start()
        self.mock_open = patch('builtins.open', mock_open()).start()
        self.m = mock_open(read_data='firmware')
        self.m = test_binary_reading()
        self.addCleanup(patch.stopall)

    def test_values(self):
        return "mtd_dev_path", 100, 100, "mtd_name"

    def test_binary_reading(self):
        return b'firmware'

    def test_env_firmware_write(self):
        self.mock_mtd_device.return_value.get_mtd_info.return_value = self.test_values()
        self.mock_os_path_getsize.return_value = 100

        with patch('builtins.open', self.m, create=True):
            env_firmware = EnvFirmware('firmware', self.m)
            try:
                env_firmware.write()
            except UpgradeError:
                self.fail("EnvFirmware.write() raised UpgradeError unexpectedly!")

    def test_env_firmware_write_raises_subprocess_error(self):
        self.mock_mtd_device.return_value.get_mtd_info.return_value = self.test_values()
        self.mock_os_path_getsize.return_value = 100
        self.mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, 'cmd')

        with patch('builtins.open', self.m, create=True):
            env_firmware = EnvFirmware('firmware', self.m)
            with self.assertRaises(UpgradeError):
                env_firmware.write()

    def test_env_firmware_write_raises_upgrade_error(self):
        self.mock_mtd_device.return_value.get_mtd_info.return_value = self.test_values()
        self.mock_os_path_getsize.return_value = 100
        self.mock_mtd_device.return_value.write.side_effect = UpgradeError('error')

        with patch('builtins.open', self.m, create=True):
            env_firmware = EnvFirmware('firmware', self.m)
            with self.assertRaises(UpgradeError):
                env_firmware.write()

    def test_env_firmware_read(self):
        self.mock_mtd_device.return_value.get_mtd_info.return_value = self.test_values()
        self.mock_mtd_device.return_value.read.return_value = b'firmware_data'

        with patch('builtins.open', self.m, create=True):
            env_firmware = EnvFirmware('firmware', self.m)
            result = env_firmware.read()

            self.assertEqual(result, b'firmware_data')

    def test_env_firmware_read_raises_upgrade_error(self):
        self.mock_mtd_device.return_value.get_mtd_info.return_value = self.test_values()
        self.mock_mtd_device.return_value.read.side_effect = UpgradeError('error')

        with patch('builtins.open', self.m, create=True):
            env_firmware = EnvFirmware('firmware', self.m)
            with self.assertRaises(UpgradeError):
                env_firmware.read()

if __name__ == '__main__':
    unittest.main()
