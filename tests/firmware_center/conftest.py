# SPDX-License-Identifier: MIT

import importlib.machinery
import importlib.util
import sys
import types
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_FWU = REPO_ROOT / "meta-example/recipes-app/iot2050-firmware-update/files/iot2050-firmware-update.tmpl"
SYSTEM_FWU_CLI = REPO_ROOT / "meta-example/recipes-app/iot2050-firmware-update/files/iot2050-firmware-update-cli"
MODULE_FWU = REPO_ROOT / "meta-sm/recipes-app/iot2050-module-firmware-update/files/iot2050-module-firmware-update.tmpl"
MODULE_FWU_CORE = REPO_ROOT / "meta-sm/recipes-app/iot2050-module-firmware-update/files/iot2050_module_firmware_update.py"
EIO_FWU = REPO_ROOT / "meta-sm/recipes-app/iot2050-eio-manager/files/iot2050_eio_fwu.py"


def load_source(module_name, path):
    loader = importlib.machinery.SourceFileLoader(module_name, str(path))
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.fixture
def module_fwu(monkeypatch):
    core = load_source("iot2050_module_firmware_update", MODULE_FWU_CORE)
    monkeypatch.setitem(sys.modules, "iot2050_module_firmware_update", core)
    cli = load_source("module_fwu_under_test", MODULE_FWU)
    cli.core = core
    return cli


@pytest.fixture
def system_fwu(monkeypatch, tmp_path):
    progress = types.ModuleType("progress")
    progress_bar = types.ModuleType("progress.bar")

    class DummyBar:
        def __init__(self, *args, **kwargs):
            pass

        def next(self):
            pass

        def finish(self):
            pass

    progress_bar.Bar = DummyBar
    progress.bar = progress_bar
    monkeypatch.setitem(sys.modules, "progress", progress)
    monkeypatch.setitem(sys.modules, "progress.bar", progress_bar)

    source = SYSTEM_FWU.read_text(encoding="utf-8").replace('${PV}', "1.1.1")
    generated = tmp_path / "iot2050_firmware_update.py"
    generated.write_text(source, encoding="utf-8")
    return load_source("system_fwu_under_test", generated)


@pytest.fixture
def eio_fwu(monkeypatch):
    gpiod = types.ModuleType("gpiod")
    gpiod_line = types.ModuleType("gpiod.line")

    class Direction:
        OUTPUT = object()

    class Value:
        ACTIVE = object()
        INACTIVE = object()

    gpiod_line.Direction = Direction
    gpiod_line.Value = Value
    gpiod.line = gpiod_line
    monkeypatch.setitem(sys.modules, "gpiod", gpiod)
    monkeypatch.setitem(sys.modules, "gpiod.line", gpiod_line)

    globals_stub = types.ModuleType("iot2050_eio_global")
    globals_stub.EIO_FS_FW_VER = "/nonexistent/eio-version"
    globals_stub.EIO_FWU_META = "/nonexistent/firmware-version"
    globals_stub.EIO_FWU_MAP3_FW_BIN = "/nonexistent/map3-fw.bin"
    monkeypatch.setitem(sys.modules, "iot2050_eio_global", globals_stub)

    return load_source("eio_fwu_under_test", EIO_FWU)
