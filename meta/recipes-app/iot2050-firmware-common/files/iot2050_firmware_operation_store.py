# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""Small durable store for domain firmware operation state."""

import json
import os
import queue
import fcntl
import threading
from collections import deque
from datetime import datetime, timezone
import uuid
from pathlib import Path


class FirmwareOperationLogHub:
    """Publish volatile operation logs to live subscribers."""

    _CLOSED = object()

    def __init__(self, max_entries=32, queue_size=32):
        self.max_entries = max_entries
        self.queue_size = queue_size
        self._lock = threading.Lock()
        self._operations = {}

    def _operation(self, operation_id):
        return self._operations.setdefault(
            operation_id, {"next_sequence": 1, "entries": deque(),
                           "subscribers": set(), "closed": False}
        )

    def publish(self, operation_id, message):
        entry = None
        with self._lock:
            operation = self._operation(operation_id)
            if operation["closed"]:
                return
            entry = {
                "sequence": operation["next_sequence"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": str(message),
            }
            operation["next_sequence"] += 1
            operation["entries"].append(entry)
            while len(operation["entries"]) > self.max_entries:
                operation["entries"].popleft()
            for subscriber in tuple(operation["subscribers"]):
                try:
                    subscriber.put_nowait(entry)
                except queue.Full:
                    try:
                        subscriber.get_nowait()
                    except queue.Empty:
                        pass
                    try:
                        subscriber.put_nowait({
                            "sequence": entry["sequence"],
                            "timestamp": entry["timestamp"],
                            "message": "Some progress messages were skipped",
                        })
                    except queue.Full:
                        pass

    def subscribe(self, operation_id, after_sequence=0):
        subscriber = queue.Queue(maxsize=self.queue_size)
        with self._lock:
            operation = self._operation(operation_id)
            entries = [
                entry for entry in operation["entries"]
                if entry["sequence"] > after_sequence
            ]
            if operation["closed"]:
                subscriber.put_nowait(self._CLOSED)
            else:
                operation["subscribers"].add(subscriber)
        return subscriber, entries

    def unsubscribe(self, operation_id, subscriber):
        with self._lock:
            operation = self._operations.get(operation_id)
            if operation is not None:
                operation["subscribers"].discard(subscriber)

    def close(self, operation_id):
        with self._lock:
            operation = self._operations.get(operation_id)
            if operation is None:
                return
            operation["closed"] = True
            for subscriber in tuple(operation["subscribers"]):
                try:
                    subscriber.put_nowait(self._CLOSED)
                except queue.Full:
                    try:
                        subscriber.get_nowait()
                        subscriber.put_nowait(self._CLOSED)
                    except queue.Empty:
                        pass
            operation["subscribers"].clear()

    def is_closed(self, operation_id):
        with self._lock:
            operation = self._operations.get(operation_id)
            return operation is not None and operation["closed"]


class FirmwareOperationStore:
    """Persist operation state without duplicating the durable task store."""

    SCHEMA_VERSION = 1
    TRANSIENT_FIELDS = {"stage", "recent_events", "next_sequence"}

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

    def _admission_lock(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        os.chmod(self.directory, 0o700)
        lock_path = self.directory / ".admission.lock"
        lock_file = lock_path.open("a+")
        os.chmod(lock_path, 0o600)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        return lock_file

    def _has_running_unlocked(self):
        for path in self.directory.glob("*.json"):
            try:
                operation = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if operation.get("state") == "running":
                return True
        return False

    def admit(self, operation_id, operation):
        """Atomically reject a running operation or create a new one."""
        lock_file = self._admission_lock()
        try:
            if self._has_running_unlocked():
                return False
            self.create(operation_id, operation)
            return True
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()

    def create(self, operation_id, operation):
        now = datetime.now(timezone.utc).isoformat()
        for field in self.TRANSIENT_FIELDS:
            operation.pop(field, None)
        operation.setdefault("schema_version", self.SCHEMA_VERSION)
        operation.setdefault("created_at", now)
        operation.setdefault("updated_at", now)
        self._write(operation_id, operation)

    def update(self, operation_id, **values):
        operation = self.read(operation_id)
        for field in self.TRANSIENT_FIELDS:
            values.pop(field, None)
        operation.update(values)
        for field in self.TRANSIENT_FIELDS:
            operation.pop(field, None)
        operation["schema_version"] = self.SCHEMA_VERSION
        now = datetime.now(timezone.utc).isoformat()
        operation["updated_at"] = now
        if operation.get("state") in {
                "succeeded", "failed", "interrupted"}:
            operation.setdefault("finished_at", now)
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
        lock_file = self._admission_lock()
        try:
            return self._has_running_unlocked()
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()

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
                    "schema_version": self.SCHEMA_VERSION,
                    "state": "interrupted",
                    "ok": False,
                    "code": "operation-interrupted",
                    "message": (
                        "Firmware service stopped before the operation completed"
                    ),
                    "last_message": (
                        "Firmware service stopped before the operation completed"
                    ),
                    "error": {
                        "code": "operation-interrupted",
                        "message": (
                            "Firmware service stopped before the operation completed"
                        ),
                    },
                })
                now = datetime.now(timezone.utc).isoformat()
                operation["updated_at"] = now
                operation["finished_at"] = now
                self._write(path.stem, operation)
            except (OSError, ValueError, KeyError):
                continue
