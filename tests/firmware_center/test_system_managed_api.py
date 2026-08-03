# SPDX-License-Identifier: MIT

import io
import json
import tarfile

import pytest


class QuietInterface:
    def interact(self, *args):
        pytest.fail("managed inspection must not request interactive input")

    def progress_bar(self, *args, **kwargs):
        pass


def add_bytes(archive, name, content, entry_type=tarfile.REGTYPE, linkname=""):
    member = tarfile.TarInfo(name)
    member.type = entry_type
    member.linkname = linkname
    member.size = len(content) if entry_type == tarfile.REGTYPE else 0
    archive.addfile(member, io.BytesIO(content) if member.size else None)


def create_package(path, firmware_name="firmware.bin"):
    config = json.dumps({
        "firmware": [{
            "name": firmware_name,
            "version": "V02.00.00",
            "description": "Test firmware",
            "type": "uboot",
            "target_boards": ["test-board"],
        }],
        "suggest_preserved_uboot_env": [],
    }).encode()
    with tarfile.open(path, "w:xz") as archive:
        add_bytes(archive, firmware_name, b"firmware")
        add_bytes(archive, firmware_name + ".sig", b"signature")
        add_bytes(archive, "u-boot-initial-env", b"boot_targets=mmc0\n")
        add_bytes(archive, "update.conf.json", config)


@pytest.mark.parametrize(
    ("name", "entry_type", "linkname"),
    [
        ("../outside", tarfile.REGTYPE, ""),
        ("/absolute", tarfile.REGTYPE, ""),
        ("link", tarfile.SYMTYPE, "/etc/passwd"),
        ("hardlink", tarfile.LNKTYPE, "update.conf.json"),
        ("nested/file", tarfile.REGTYPE, ""),
    ],
)
def test_firmware_package_rejects_unsafe_members(
    system_fwu, tmp_path, name, entry_type, linkname
):
    package_path = tmp_path / "unsafe.tar"
    with tarfile.open(package_path, "w") as archive:
        add_bytes(archive, name, b"unsafe", entry_type, linkname)

    with package_path.open("rb") as package_file:
        with pytest.raises(system_fwu.UpgradeError) as error:
            system_fwu.FirmwareTarball(
                package_file, QuietInterface(), None, True)

    assert error.value.code == system_fwu.ErrorCode.INVALID_FIRMWARE.value


def test_firmware_package_rejects_malformed_tar(system_fwu, tmp_path):
    package_path = tmp_path / "malformed.tar.xz"
    package_path.write_bytes(b"not a tar archive")

    with pytest.raises(system_fwu.UpgradeError) as error:
        system_fwu.inspect_system_firmware(package_path)

    assert error.value.code == system_fwu.ErrorCode.INVALID_FIRMWARE.value


def test_managed_inspection_returns_metadata_and_cleans_private_directory(
    system_fwu, monkeypatch, tmp_path
):
    package_path = tmp_path / "firmware.tar.xz"
    create_package(package_path)

    class FakeBoardInfo:
        board_name = "test-board"
        os_info = {}

    extracted_directory = None

    def verified(package, firmware_name):
        nonlocal extracted_directory
        extracted_directory = package.extract_path
        assert firmware_name == "firmware.bin"

    monkeypatch.setattr(system_fwu, "BoardInfo", FakeBoardInfo)
    monkeypatch.setattr(
        system_fwu.FirmwareTarball,
        "verify_firmware_signature",
        verified,
    )

    details = system_fwu.inspect_system_firmware(package_path)

    assert details["target_version"] == "V02.00.00"
    assert details["signature_verified"] is True
    assert len(details["firmware_sha256"]) == 64
    assert not system_fwu.os.path.exists(extracted_directory)
