# SPDX-License-Identifier: MIT

import json
import os
import sys
import tarfile

import pytest


def run_main(system_fwu, monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)
    return system_fwu.main(argv)


def test_error_codes_are_stable(system_fwu):
    assert {code.name: code.value for code in system_fwu.ErrorCode} == {
        "SUCCESS": 0,
        "ROLLBACK_SUCCESS": 1,
        "INVALID_ARG": 2,
        "BACKUP_FAILED": 3,
        "ROLLBACK_FAILED": 4,
        "FLASHING_FAILED": 5,
        "CANCELED": 6,
        "INVALID_FIRMWARE": 7,
        "FAILED": 8,
        "MISSING_SIGNATURE": 9,
        "MISSING_PUBLIC_KEY": 10,
        "BAD_SIGNATURE": 11,
    }


def test_requires_firmware_unless_rollback(system_fwu, monkeypatch, capsys):
    assert run_main(system_fwu, monkeypatch, ["iot2050-firmware-update"]) == 2
    assert "A firmware tarball is required" in capsys.readouterr().err


def test_force_and_verify_are_mutually_exclusive(
    system_fwu, monkeypatch, tmp_path, capsys
):
    firmware = tmp_path / "firmware.bin"
    firmware.write_bytes(b"firmware")

    with pytest.raises(SystemExit) as error:
        run_main(system_fwu, monkeypatch, [
            "iot2050-firmware-update", "--force", "--verify", str(firmware)
        ])

    assert error.value.code == 2
    assert "not allowed with" in capsys.readouterr().err


def test_force_and_no_backup_are_rejected(system_fwu, monkeypatch, tmp_path):
    firmware = tmp_path / "firmware.bin"
    firmware.write_bytes(b"firmware")

    with pytest.raises(SystemExit) as error:
        run_main(system_fwu, monkeypatch, [
            "iot2050-firmware-update", "--force", "--no-backup", str(firmware)
        ])

    assert error.value.code == 2


def test_user_can_cancel_before_hardware_access(
    system_fwu, monkeypatch, tmp_path
):
    firmware = tmp_path / "firmware.tar.xz"
    firmware.write_bytes(b"placeholder")

    class FakeTarball:
        def __init__(self, *args, **kwargs):
            pass

        def check_firmware(self):
            return True

    class FakeUI:
        def __init__(self, quiet):
            pass

        def interact(self, expected, message):
            return "n"

    class UnexpectedUpdater:
        def __init__(self, *args, **kwargs):
            pytest.fail("updater must not be constructed before confirmation")

    monkeypatch.setattr(system_fwu, "FirmwareTarball", FakeTarball)
    monkeypatch.setattr(system_fwu, "UserInterface", FakeUI)
    monkeypatch.setattr(system_fwu, "FirmwareUpdate", UnexpectedUpdater)

    assert run_main(system_fwu, monkeypatch, [
        "iot2050-firmware-update", str(firmware)
    ]) == system_fwu.ErrorCode.CANCELED.value


@pytest.mark.parametrize(
    ("include_signature", "include_public_key", "expected_code"),
    [
        (False, True, 9),
        (True, False, 10),
    ],
)
@pytest.mark.filterwarnings("ignore:unclosed file.*update.conf.json:ResourceWarning")
def test_verify_missing_artifacts_use_real_tarball_validation(
    system_fwu, monkeypatch, tmp_path, include_signature,
    include_public_key, expected_code
):
    unique = tmp_path.name
    firmware_name = f"{unique}-firmware.bin"
    config_name = "update.conf.json"
    env_name = "u-boot-initial-env"
    archive = tmp_path / "firmware.tar.xz"
    firmware = tmp_path / firmware_name
    config = tmp_path / config_name
    environment = tmp_path / env_name
    signature = tmp_path / f"{firmware_name}.sig"
    public_key = tmp_path / "public.key"
    firmware.write_bytes(b"firmware")
    config.write_text(json.dumps({
        "firmware": [{
            "name": firmware_name,
            "type": "uboot",
            "target_boards": ["test-board"],
        }],
        "suggest_preserved_uboot_env": [],
    }), encoding="utf-8")
    environment.write_text("boot_targets=mmc0\n", encoding="utf-8")
    if include_signature:
        signature.write_bytes(b"signature")
    if include_public_key:
        public_key.write_bytes(b"unused-public-key")

    with tarfile.open(archive, "w:xz") as tar:
        tar.add(firmware, arcname=firmware_name)
        tar.add(config, arcname=config_name)
        tar.add(environment, arcname=env_name)
        if include_signature:
            tar.add(signature, arcname=signature.name)

    class FakeBoardInfo:
        board_name = "test-board"
        os_info = {}

    class FakeUI:
        def __init__(self, quiet):
            pass

        def interact(self, expected, message):
            return "y"

    class VerifyingUpdater:
        def __init__(self, tarball, *args, **kwargs):
            self.tarball = tarball

        def backup(self):
            pass

        def update(self):
            try:
                name = self.tarball.get_file_name("uboot")
                self.tarball.verify_firmware_signature(name)
            finally:
                self.tarball.firmware_tarball.close()
                self.tarball.__del__()
                self.tarball.extracted_files = []

    monkeypatch.setattr(system_fwu, "BoardInfo", FakeBoardInfo)
    monkeypatch.setattr(system_fwu, "UserInterface", FakeUI)
    monkeypatch.setattr(system_fwu, "FirmwareUpdate", VerifyingUpdater)
    monkeypatch.setattr(
        system_fwu.FirmwareTarball, "PUBLIC_KEY_PATH", str(public_key)
    )

    try:
        assert run_main(system_fwu, monkeypatch, [
            "iot2050-firmware-update", "--verify", str(archive)
        ]) == expected_code
    finally:
        for name in (firmware_name, config_name, env_name, signature.name):
            path = os.path.join("/tmp", name)
            if os.path.exists(path):
                os.remove(path)


def test_bad_signature_is_not_retried(system_fwu, monkeypatch, tmp_path):
    firmware = tmp_path / "firmware.tar.xz"
    firmware.write_bytes(b"placeholder")
    attempts = []

    class FakeTarball:
        def __init__(self, *args, **kwargs):
            pass

        def check_firmware(self):
            return True

    class FakeUI:
        def __init__(self, quiet):
            pass

        def interact(self, expected, message):
            return "y"

    class FakeUpdater:
        def __init__(self, *args, **kwargs):
            pass

        def backup(self):
            pass

        def update(self):
            attempts.append(1)
            raise system_fwu.UpgradeError(
                "Bad firmware signature",
                system_fwu.ErrorCode.BAD_SIGNATURE.value,
            )

    monkeypatch.setattr(system_fwu, "FirmwareTarball", FakeTarball)
    monkeypatch.setattr(system_fwu, "FirmwareUpdate", FakeUpdater)
    monkeypatch.setattr(system_fwu, "UserInterface", FakeUI)

    assert run_main(system_fwu, monkeypatch, [
        "iot2050-firmware-update", "--verify", str(firmware)
    ]) == system_fwu.ErrorCode.BAD_SIGNATURE.value
    assert len(attempts) == 1


def test_generic_update_failure_is_attempted_four_times(
    system_fwu, monkeypatch, tmp_path
):
    firmware = tmp_path / "firmware.tar.xz"
    firmware.write_bytes(b"placeholder")
    attempts = []

    class FakeTarball:
        def __init__(self, *args, **kwargs):
            pass

        def check_firmware(self):
            return True

    class FakeUI:
        def __init__(self, quiet):
            pass

        def interact(self, expected, message):
            return "y"

    class FakeUpdater:
        def __init__(self, *args, **kwargs):
            pass

        def backup(self):
            pass

        def update(self):
            attempts.append(1)
            raise system_fwu.UpgradeError("write failed")

    monkeypatch.setattr(system_fwu, "FirmwareTarball", FakeTarball)
    monkeypatch.setattr(system_fwu, "FirmwareUpdate", FakeUpdater)
    monkeypatch.setattr(system_fwu, "UserInterface", FakeUI)

    assert run_main(system_fwu, monkeypatch, [
        "iot2050-firmware-update", str(firmware)
    ]) == system_fwu.ErrorCode.FAILED.value
    assert len(attempts) == 4
