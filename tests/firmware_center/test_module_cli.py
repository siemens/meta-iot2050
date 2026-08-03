# SPDX-License-Identifier: MIT

import builtins
import io


class RecordingBytesIO(io.BytesIO):
    def __init__(self, path, writes):
        super().__init__()
        self.path = path
        self.writes = writes

    def close(self):
        self.writes[self.path] = self.getvalue()
        super().close()


def test_requires_at_least_one_firmware(module_fwu, capsys):
    assert module_fwu.main(["--slot", "1"]) == 1
    output = capsys.readouterr().out
    assert "Error: No firmware file specified" in output
    assert "usage:" in output


def test_writes_firmware_a_to_selected_slot(module_fwu, tmp_path, monkeypatch, capsys):
    firmware = tmp_path / "chip-a.bin"
    firmware.write_bytes(b"firmware-a")
    writes = {}

    def fake_open(path, mode="r", *args, **kwargs):
        if path == "/eiofs/controller/slot3/fwa" and mode == "wb":
            return RecordingBytesIO(path, writes)
        return builtins.open(path, mode, *args, **kwargs)

    monkeypatch.setattr(module_fwu.core, "open", fake_open, raising=False)

    assert module_fwu.main(["--slot", "3", "--firmware-a", str(firmware)]) == 0
    assert writes["/eiofs/controller/slot3/fwa"] == b"firmware-a"
    assert "Please reboot the upgraded module" in capsys.readouterr().out


def test_writes_firmware_b_to_selected_slot(module_fwu, tmp_path, monkeypatch):
    firmware = tmp_path / "chip-b.bin"
    firmware.write_bytes(b"firmware-b")
    writes = {}

    def fake_open(path, mode="r", *args, **kwargs):
        if path == "/eiofs/controller/slot6/fwb" and mode == "wb":
            return RecordingBytesIO(path, writes)
        return builtins.open(path, mode, *args, **kwargs)

    monkeypatch.setattr(module_fwu.core, "open", fake_open, raising=False)

    assert module_fwu.main(["-s", "6", "-fwb", str(firmware)]) == 0
    assert writes["/eiofs/controller/slot6/fwb"] == b"firmware-b"


def test_writes_both_chip_firmwares(module_fwu, tmp_path, monkeypatch):
    firmware_a = tmp_path / "chip-a.bin"
    firmware_b = tmp_path / "chip-b.bin"
    firmware_a.write_bytes(b"a")
    firmware_b.write_bytes(b"b")
    writes = {}

    def fake_open(path, mode="r", *args, **kwargs):
        if path.startswith("/eiofs/controller/slot2/") and mode == "wb":
            return RecordingBytesIO(path, writes)
        return builtins.open(path, mode, *args, **kwargs)

    monkeypatch.setattr(module_fwu.core, "open", fake_open, raising=False)

    assert module_fwu.main([
        "--slot", "2",
        "--firmware-a", str(firmware_a),
        "--firmware-b", str(firmware_b),
    ]) == 0
    assert writes["/eiofs/controller/slot2/fwa"] == b"a"
    assert writes["/eiofs/controller/slot2/fwb"] == b"b"


def test_stops_and_returns_failure_when_chip_a_write_fails(
    module_fwu, tmp_path, monkeypatch, capsys
):
    firmware_a = tmp_path / "chip-a.bin"
    firmware_b = tmp_path / "chip-b.bin"
    firmware_a.write_bytes(b"a")
    firmware_b.write_bytes(b"b")
    opened_paths = []

    def fake_open(path, mode="r", *args, **kwargs):
        if path.startswith("/eiofs/controller/"):
            opened_paths.append(path)
            raise OSError("write denied")
        return builtins.open(path, mode, *args, **kwargs)

    monkeypatch.setattr(module_fwu.core, "open", fake_open, raising=False)

    assert module_fwu.main([
        "-s", "1",
        "-fwa", str(firmware_a),
        "-fwb", str(firmware_b),
    ]) == 1
    assert opened_paths == ["/eiofs/controller/slot1/fwa"]
    assert "Failed to write firmware A" in capsys.readouterr().out


def test_reports_failure_after_chip_a_succeeds_and_chip_b_fails(
    module_fwu, tmp_path, monkeypatch, capsys
):
    firmware_a = tmp_path / "chip-a.bin"
    firmware_b = tmp_path / "chip-b.bin"
    firmware_a.write_bytes(b"a")
    firmware_b.write_bytes(b"b")
    writes = {}

    def fake_open(path, mode="r", *args, **kwargs):
        if path == "/eiofs/controller/slot4/fwa":
            return RecordingBytesIO(path, writes)
        if path == "/eiofs/controller/slot4/fwb":
            raise OSError("chip B unavailable")
        return builtins.open(path, mode, *args, **kwargs)

    monkeypatch.setattr(module_fwu.core, "open", fake_open, raising=False)

    assert module_fwu.main([
        "-s", "4",
        "-fwa", str(firmware_a),
        "-fwb", str(firmware_b),
    ]) == 1
    assert writes["/eiofs/controller/slot4/fwa"] == b"a"
    assert "Failed to write firmware B" in capsys.readouterr().out
