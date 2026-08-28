# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""Small durable store for domain firmware operation state."""

import json
import os
import threading
import uuid
from pathlib import Path


class FirmwareOperationStore:
    """Persist operation state without duplicating the durable task store."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self._lock = threading.Lock()

    def _path(self, operation_id):
        try:
            normalized = str(uuid.UUID(operation_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError("Invalid firmware operation ID") from error
        return self.directory / f"{normalized}.json"

    def _write(self, operation_id, operation):
        self.directory.mkdir(parents=True, exist_ok=True)
        os.chmod(self.directory, 0o700)
        path = self._path(operation_id)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        try:
            with self._lock:
                temporary.write_text(
                    json.dumps(operation, separators=(",", ":"), sort_keys=True),
                    encoding="utf-8",
                )
                os.chmod(temporary, 0o600)
                os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    def create(self, operation_id, operation):
        self._write(operation_id, operation)

    def update(self, operation_id, **values):
        operation = self.read(operation_id)
        operation.update(values)
        self._write(operation_id, operation)

    def read(self, operation_id):
        path = self._path(operation_id)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise KeyError(operation_id) from error

    def has_running(self):
        """Return True when any stored operation is still running."""
        if not self.directory.is_dir():
            return False
        for path in self.directory.glob("*.json"):
            try:
                operation = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if operation.get("state") == "running":
                return True
        return False

    def recover_running(self):
        """Mark operations interrupted by a service restart as failed."""
        if not self.directory.is_dir():
            return
        for path in self.directory.glob("*.json"):
            try:
                operation = json.loads(path.read_text(encoding="utf-8"))
                if operation.get("state") != "running":
                    continue
                operation.update({
                    "state": "failed",
                    "ok": False,
                    "code": "operation-interrupted",
                    "message": (
                        "Firmware service stopped before the operation completed"
                    ),
                    "details_json": "",
                })
                self._write(path.stem, operation)
            except (OSError, ValueError, KeyError):
                continue
