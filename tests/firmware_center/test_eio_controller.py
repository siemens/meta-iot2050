# SPDX-License-Identifier: MIT

import hashlib
import json

import pytest


def configure_checker_paths(eio_fwu, monkeypatch, tmp_path, current_version=None,
                            bundled_version="2.0.0", firmware=b"map3-firmware",
                            sha1sum=None):
    current = tmp_path / "current-version"
    metadata = tmp_path / "firmware-version"
    binary = tmp_path / "map3-fw.bin"

    if current_version is not None:
        current.write_text(f"{current_version} extra fields\n", encoding="ascii")
    binary.write_bytes(firmware)
    metadata.write_text(json.dumps({
        "version": bundled_version,
        "sha1sum": sha1sum or hashlib.sha1(firmware).hexdigest(),
    }), encoding="ascii")

    monkeypatch.setattr(eio_fwu, "EIO_FS_FW_VER", str(current))
    monkeypatch.setattr(eio_fwu, "EIO_FWU_META", str(metadata))
    monkeypatch.setattr(eio_fwu, "EIO_FWU_MAP3_FW_BIN", str(binary))
    return current, metadata, binary


def test_reports_up_to_date(eio_fwu, monkeypatch, tmp_path):
    current, metadata, binary = configure_checker_paths(
        eio_fwu, monkeypatch, tmp_path,
        current_version="2.0.0", bundled_version="2.0.0",
    )

    checker = eio_fwu.FirmwareUpdateChecker(
        str(current), str(metadata), str(binary))
    status, message = checker.collect_fwu_info()

    assert status == 0
    assert "up-to-date" in message
    inspection = checker.inspect()
    assert inspection["status"] == "up-to-date"
    assert inspection["current_version"] == "2.0.0"
    assert inspection["bundled_version"] == "2.0.0"
    assert inspection["integrity"] is True
    assert inspection["update_needed"] is False
    assert inspection["actual_sha256"] == hashlib.sha256(
        b"map3-firmware").hexdigest()


def test_reports_update_when_version_differs_and_hash_matches(
    eio_fwu, monkeypatch, tmp_path
):
    configure_checker_paths(
        eio_fwu, monkeypatch, tmp_path,
        current_version="1.0.0", bundled_version="2.0.0",
    )

    status, message = eio_fwu.FirmwareUpdateChecker().collect_fwu_info()

    assert status == 1
    assert "need update" in message


def test_reports_corrupt_bundled_firmware_when_hash_mismatches(
    eio_fwu, monkeypatch, tmp_path
):
    configure_checker_paths(
        eio_fwu, monkeypatch, tmp_path,
        current_version="1.0.0", bundled_version="2.0.0",
        sha1sum="0" * 40,
    )

    status, message = eio_fwu.FirmwareUpdateChecker().collect_fwu_info()

    assert status == 2
    assert "checksum does not match" in message


def test_reports_missing_runtime_version(eio_fwu, monkeypatch, tmp_path):
    configure_checker_paths(eio_fwu, monkeypatch, tmp_path, current_version=None)

    status, message = eio_fwu.FirmwareUpdateChecker().collect_fwu_info()

    assert status == 1
    assert "EIO FUSE does not exist" in message


def test_malformed_metadata_preserves_current_exception_contract(
    eio_fwu, monkeypatch, tmp_path
):
    current = tmp_path / "current-version"
    metadata = tmp_path / "firmware-version"
    binary = tmp_path / "map3-fw.bin"
    current.write_text("1.0.0\n", encoding="ascii")
    metadata.write_text("not-json", encoding="ascii")
    binary.write_bytes(b"firmware")
    monkeypatch.setattr(eio_fwu, "EIO_FS_FW_VER", str(current))
    monkeypatch.setattr(eio_fwu, "EIO_FWU_META", str(metadata))
    monkeypatch.setattr(eio_fwu, "EIO_FWU_MAP3_FW_BIN", str(binary))

    with pytest.raises(json.JSONDecodeError):
        eio_fwu.FirmwareUpdateChecker()

    inspection = eio_fwu.FirmwareUpdateChecker(
        str(current), str(metadata), str(binary), strict=False).inspect()
    assert inspection["status"] == "unavailable"
    assert inspection["integrity"] is None
    assert "metadata" in inspection["message"]


def test_missing_bundled_binary_is_structured_in_non_strict_mode(
    eio_fwu, tmp_path
):
    current = tmp_path / "current-version"
    metadata = tmp_path / "firmware-version"
    binary = tmp_path / "missing-map3-fw.bin"
    current.write_text("1.0.0\n", encoding="ascii")
    metadata.write_text(json.dumps({
        "version": "2.0.0",
        "sha1sum": "0" * 40,
    }), encoding="ascii")

    inspection = eio_fwu.FirmwareUpdateChecker(
        str(current), str(metadata), str(binary), strict=False).inspect()

    assert inspection["status"] == "unavailable"
    assert inspection["current_version"] == "1.0.0"
    assert inspection["bundled_version"] == "2.0.0"
    assert inspection["integrity"] is None
    assert "binary is missing" in inspection["message"]


def test_update_firmware_maps_upgrade_error(eio_fwu, monkeypatch):
    class FailingUpdate:
        def __init__(self, firmware, entity):
            pass

        def update(self):
            raise eio_fwu.UpgradeError("flash failed")

    monkeypatch.setattr(eio_fwu, "FirmwareUpdate", FailingUpdate)

    status, error = eio_fwu.update_firmware(b"firmware", 0)

    assert status == 1
    assert str(error) == "flash failed"


def test_readback_digest_mismatch_is_rejected(eio_fwu):
    updater = object.__new__(eio_fwu.FirmwareUpdate)

    class FakeFirmware:
        write_firmware = b"expected"

        def write(self):
            pass

        def read(self):
            return b"different"

    updater.firmwares = {0: FakeFirmware()}

    with pytest.raises(eio_fwu.UpgradeError, match="digest verification failed"):
        updater.update()


def test_eio_firmware_releases_gpio_and_flash_resources(eio_fwu):
    events = []

    class PinRequest:
        def set_value(self, offset, value):
            events.append(("set", offset, value))

        def release(self):
            events.append(("pin-release",))

    class FlashProgrammer:
        def release(self):
            events.append(("flash-release",))

    firmware = object.__new__(eio_fwu.EIOFirmware)
    firmware.spi_mux_pin_request = PinRequest()
    firmware.spi_mux_pin_offset = 7
    firmware.flash_prog = FlashProgrammer()

    firmware.__del__()
    firmware.spi_mux_pin_request = None
    firmware.flash_prog = None

    assert events == [
        ("set", 7, eio_fwu.Value.INACTIVE),
        ("pin-release",),
        ("flash-release",),
    ]
