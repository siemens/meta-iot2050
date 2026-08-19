# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""Core protocol and backend registry for the IOT2050 firmware task core."""

import contextlib
import fcntl
import importlib.util
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import grpc

from iot2050_system_firmware_pb2 import (
    InspectRequest,
    OperationRequest,
    RollbackRequest,
    UpdateRequest,
)
from iot2050_system_firmware_pb2_grpc import SystemFirmwareStub
from iot2050_firmware_global import (
    DEFAULT_FIRMWARE_DIR,
    DEFAULT_FIRMWARE_PATTERN,
    DEFAULT_MAX_FIRMWARE_SIZE,
    SYSTEM_FIRMWARE_SOCKET_TARGET as SYSTEM_FIRMWARE_SOCKET,
)


PROTOCOL_VERSION = 1
DEFAULT_BACKEND_DIR = "/usr/lib/iot2050/fwmgr/backends.d"
DEFAULT_TASK_DIR = "/var/lib/iot2050-fwmgr/tasks"
DEFAULT_STAGING_DIR = "/var/lib/iot2050-fwmgr/staging"
TASK_ADMISSION_LOCK = "/run/iot2050/firmware-task-admission.lock"
TASK_UNIT = "iot2050-firmware-task@{}.service"


class FirmwareError(Exception):
    """A stable error returned through the firmware IPC."""

    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


class SystemFirmwareBackend:
    name = "system"

    def __init__(self, backup_dir=None,
                 firmware_dir=DEFAULT_FIRMWARE_DIR):
        self.backup_dir = Path(backup_dir) if backup_dir else None
        self.firmware_dir = Path(firmware_dir)
        self.staging_store = None

    def bind_staging_store(self, staging_store):
        self.staging_store = staging_store

    def available(self):
        return True, None

    def capabilities(self):
        default_package = self._default_package()
        return {
            "backend": self.name,
            "label": "System Firmware",
            "operations": ["inspect", "update", "rollback"],
            "source": ["image-default", "upload"],
            "requires_signature": True,
            "rollback_source": "shared-local-backup",
            "default_package": default_package.name if default_package else None,
        }

    def _default_package(self):
        candidates = sorted(
            path for path in self.firmware_dir.glob(DEFAULT_FIRMWARE_PATTERN)
            if path.is_file() and not path.is_symlink()
        )
        return candidates[-1] if candidates else None

    @staticmethod
    def _system_stub():
        channel = grpc.insecure_channel(SYSTEM_FIRMWARE_SOCKET)
        return channel, SystemFirmwareStub(channel)

    @staticmethod
    def _system_response(response):
        if not response.ok:
            raise FirmwareError(response.code, response.message)
        try:
            return json.loads(response.details_json) if response.details_json else {}
        except ValueError as error:
            raise FirmwareError(
                "system-firmware-invalid-response",
                "System Firmware service returned invalid response data",
            ) from error

    @staticmethod
    def _wait_system_operation(stub, operation_id, progress=None, timeout=3600):
        deadline = time.monotonic() + timeout
        while True:
            response = stub.GetOperation(
                OperationRequest(operation_id=operation_id), timeout=10)
            if response.state == "running":
                if time.monotonic() >= deadline:
                    raise FirmwareError(
                        "system-update-timeout",
                        "System firmware update timed out",
                    )
                if progress and response.stage:
                    progress(response.stage)
                time.sleep(1)
                continue
            if not response.ok:
                raise FirmwareError(response.code, response.message)
            try:
                return json.loads(response.details_json) if response.details_json else {}
            except ValueError as error:
                raise FirmwareError(
                    "system-firmware-invalid-response",
                    "System Firmware service returned invalid operation data",
                ) from error

    def inspect(self, request):
        path, package = self._resolve(request)
        try:
            channel, stub = self._system_stub()
            try:
                response = stub.Inspect(
                    InspectRequest(firmware_path=str(path), pg2_only=True),
                    timeout=10,
                )
            finally:
                channel.close()
            details = self._system_response(response)
        except grpc.RpcError as error:
            raise FirmwareError(
                "system-firmware-service-unavailable",
                "System Firmware service is unavailable",
            ) from error
        result = {**details, "package": package}
        if request.get("device_info"):
            result["device_info"] = self._device_info()
        return result

    @staticmethod
    def _device_info():
        values = {}
        try:
            result = subprocess.run(
                ["/usr/bin/fw_printenv"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    key, separator, value = line.partition("=")
                    if separator:
                        values[key.strip()] = value.strip()
        except OSError:
            pass

        os_release = {}
        try:
            with open("/etc/os-release", encoding="utf-8") as release:
                for line in release:
                    key, separator, value = line.rstrip().partition("=")
                    if separator:
                        os_release[key] = value.strip().strip('"')
        except OSError:
            pass

        return {
            "name": values.get("board_name"),
            "mlfb": values.get("mlfb"),
            "serial": values.get("board_serial"),
            "os_image_version": SystemFirmwareBackend._version_label(
                os_release.get("BUILD_ID")
                or os_release.get("IMAGE_VERSION")
                or os_release.get("VERSION_ID")
            ),
            "firmware_version": SystemFirmwareBackend._version_label(
                values.get("fw_version")
            ),
        }

    @staticmethod
    def _version_label(value):
        if not value:
            return None
        match = re.search(r"V[0-9]+(?:\.[0-9]+)+(?:-[0-9A-Za-z._+-]+)?", value)
        return match.group(0) if match else value

    def start(self, request, progress, staging_store):
        path, package = self._resolve(request, staging_store)
        try:
            progress("checking-compatibility-and-signature")
            channel, stub = self._system_stub()
            try:
                response = stub.StartUpdate(
                    UpdateRequest(
                        firmware_path=str(path),
                        backup_dir=str(self.backup_dir) if self.backup_dir else "",
                        preserve_list=request.get("preserve_list") or [],
                        reset=bool(request.get("reset", False)),
                        pg2_only=True,
                    ),
                    timeout=10,
                )
                if not response.ok:
                    raise FirmwareError(response.code, response.message)
                result = self._wait_system_operation(
                    stub, response.operation_id, progress)
            finally:
                channel.close()
        except grpc.RpcError as error:
            raise FirmwareError(
                "system-firmware-service-unavailable",
                "System Firmware service is unavailable",
            ) from error
        return {**result, "package": package}

    def inspect_rollback(self, request):
        try:
            channel, stub = self._system_stub()
            try:
                response = stub.InspectRollback(RollbackRequest(), timeout=10)
            finally:
                channel.close()
            return self._system_response(response)
        except grpc.RpcError as error:
            raise FirmwareError(
                "system-firmware-service-unavailable",
                "System Firmware service is unavailable",
            ) from error

    def rollback(self, request, progress, staging_store):
        try:
            channel, stub = self._system_stub()
            try:
                response = stub.StartRollback(RollbackRequest(), timeout=10)
                if not response.ok:
                    raise FirmwareError(response.code, response.message)
                result = self._wait_system_operation(
                    stub, response.operation_id, progress)
            finally:
                channel.close()
            return result
        except grpc.RpcError as error:
            raise FirmwareError(
                "system-firmware-service-unavailable",
                "System Firmware service is unavailable",
            ) from error

    def _resolve(self, request, staging_store=None):
        if request.get("source") == "image-default":
            package = self._default_package()
            if package is None:
                raise FirmwareError(
                    "default-firmware-unavailable",
                    "The image-default system firmware package is unavailable",
                )
            return package, {
                "source": "image-default",
                "name": package.name,
            }
        store = staging_store or self.staging_store
        token = request.get("token")
        if store is None or not token:
            raise FirmwareError(
                "staging-required", "A staged system firmware package is required")
        path, metadata = store.resolve(token)
        return path, {"source": "upload", **metadata}

    @staticmethod
    def _raise_update_error(error):
        # Keep updater internals and paths out of the IPC while preserving the
        # stable numeric code needed by support and existing CLI documentation.
        code = getattr(error, "code", None)
        if code is None:
            raise FirmwareError(
                "system-update-failed", "System firmware operation failed"
            ) from error
        messages = {
            3: "System firmware backup failed",
            5: "System firmware flashing or readback failed",
            7: "The firmware package is not compatible with this device",
            9: "The firmware signature is missing",
            10: "The firmware verification key is unavailable",
            11: "The firmware signature is invalid",
        }
        if code in (7, 9, 10, 11) and getattr(error, "err", None):
            message = str(error.err)
        else:
            message = messages.get(code, "System firmware operation was rejected")
        raise FirmwareError(
            "system-update-rejected",
            message,
            {"updater_code": code},
        ) from error


class BackendRegistry:
    def __init__(self, backend_dir=DEFAULT_BACKEND_DIR, builtins=None):
        self.backend_dir = Path(backend_dir)
        self.backends = {}
        self.discovery_errors = []
        for backend in builtins or [SystemFirmwareBackend()]:
            self.register(backend)

    def register(self, backend):
        name = getattr(backend, "name", None)
        if not name or not isinstance(name, str):
            raise FirmwareError("invalid-backend", "Backend has no valid name")
        if name in self.backends:
            raise FirmwareError(
                "duplicate-backend", f"Backend '{name}' is already registered")
        self.backends[name] = backend

    def discover(self):
        if not self.backend_dir.is_dir():
            return
        for descriptor_path in sorted(self.backend_dir.glob("*.json")):
            try:
                descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
                module_path = descriptor_path.parent / descriptor["module"]
                class_name = descriptor["class"]
                module_name = f"iot2050_firmware_backend_{descriptor_path.stem}"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Cannot load {module_path}")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.register(getattr(module, class_name)())
            except Exception as error:
                self.discovery_errors.append({
                    "descriptor": descriptor_path.name,
                    "error": str(error),
                })
                print(
                    f"Failed to load firmware backend {descriptor_path.name}: {error}",
                    file=sys.stderr,
                )

    def available_backends(self):
        available = {}
        for name, backend in self.backends.items():
            is_available, reason = backend.available()
            if is_available:
                available[name] = backend
            elif reason:
                continue
        return available

    def visible_backends(self):
        visible = {}
        for name, backend in self.backends.items():
            is_visible = getattr(backend, "is_visible", None)
            if is_visible is not None and not is_visible():
                continue
            visible[name] = backend
        return visible

    def capabilities(self):
        capabilities = []
        for backend in self.visible_backends().values():
            capability = dict(backend.capabilities())
            try:
                is_available, reason = backend.available()
            except Exception as error:
                is_available = False
                reason = str(error)
            capability["available"] = bool(is_available)
            if not is_available:
                capability["availability_reason"] = reason or "Backend is unavailable"
            capabilities.append(capability)
        return capabilities

    def get(self, name):
        backend = self.available_backends().get(name)
        if backend is None:
            raise FirmwareError(
                "backend-unavailable", f"Backend '{name}' is unavailable")
        return backend


class TaskStore:
    def __init__(self, task_dir=DEFAULT_TASK_DIR):
        self.task_dir = Path(task_dir)
        self._lock = threading.Lock()

    def _path(self, task_id):
        try:
            normalized = str(uuid.UUID(task_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise FirmwareError("invalid-task", "Invalid task ID") from error
        return self.task_dir / f"{normalized}.json"

    def write(self, task):
        self.task_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.task_dir, 0o700)
        path = self._path(task["id"])
        temporary = path.with_suffix(".tmp")
        try:
            with self._lock:
                temporary.write_text(
                    json.dumps(task, separators=(",", ":"), sort_keys=True),
                    encoding="utf-8",
                )
                os.chmod(temporary, 0o600)
                os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    def read(self, task_id):
        path = self._path(task_id)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise FirmwareError("task-not-found", "Task was not found") from error

    def list(self):
        if not self.task_dir.is_dir():
            return []
        tasks = []
        for path in sorted(self.task_dir.glob("*.json")):
            try:
                tasks.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return tasks

class StagingStore:
    def __init__(self, staging_dir=DEFAULT_STAGING_DIR,
                 max_size=DEFAULT_MAX_FIRMWARE_SIZE):
        self.staging_dir = Path(staging_dir)
        self.max_size = max_size

    def import_file(self, source_path, label=None):
        source = Path(source_path)
        try:
            flags = os.O_RDONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            source_fd = os.open(source, flags)
            source_stat = os.fstat(source_fd)
        except OSError as error:
            raise FirmwareError("source-unavailable", "Firmware file is unavailable") from error
        if not stat.S_ISREG(source_stat.st_mode):
            os.close(source_fd)
            raise FirmwareError("invalid-source", "Firmware source is not a regular file")
        if source_stat.st_size > self.max_size:
            os.close(source_fd)
            raise FirmwareError("firmware-too-large", "Firmware file exceeds the size limit")

        token = str(uuid.uuid4())
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.staging_dir, 0o700)
        destination = self.staging_dir / token
        digest = hashlib.sha256()
        size = 0
        try:
            with os.fdopen(source_fd, "rb") as input_file, destination.open("xb") as output_file:
                os.chmod(destination, 0o600)
                while True:
                    chunk = input_file.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > self.max_size:
                        raise FirmwareError(
                            "firmware-too-large",
                            "Firmware file exceeds the size limit",
                        )
                    digest.update(chunk)
                    output_file.write(chunk)
        except Exception:
            try:
                os.close(source_fd)
            except OSError:
                pass
            destination.unlink(missing_ok=True)
            raise

        metadata = {
            "token": token,
            "name": Path(label or source.name).name,
            "size": size,
            "sha256": digest.hexdigest(),
            "created_at": time.time(),
            "last_used_at": time.time(),
            "claimed_by_task": None,
        }
        metadata_path = self.staging_dir / f"{token}.json"
        self._write_metadata(metadata_path, metadata)
        return metadata

    @staticmethod
    def _write_metadata(metadata_path, metadata):
        temporary = metadata_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(metadata, separators=(",", ":"), sort_keys=True),
            encoding="utf-8",
        )
        os.chmod(temporary, 0o600)
        os.replace(temporary, metadata_path)

    def resolve(self, token):
        try:
            normalized = str(uuid.UUID(token))
        except (ValueError, TypeError, AttributeError) as error:
            raise FirmwareError("invalid-staging-token", "Invalid staging token") from error
        path = self.staging_dir / normalized
        metadata_path = self.staging_dir / f"{normalized}.json"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise FirmwareError("staging-not-found", "Staged firmware was not found") from error
        if not path.is_file():
            raise FirmwareError("staging-not-found", "Staged firmware was not found")
        digest = hashlib.sha256()
        size = 0
        try:
            with path.open("rb") as staged_file:
                for chunk in iter(lambda: staged_file.read(1024 * 1024), b""):
                    size += len(chunk)
                    digest.update(chunk)
        except OSError as error:
            raise FirmwareError(
                "staging-unavailable", "Staged firmware is unavailable") from error
        if size != metadata.get("size") or digest.hexdigest() != metadata.get("sha256"):
            raise FirmwareError(
                "staging-integrity-failed", "Staged firmware integrity check failed")
        return path, metadata

    def _metadata(self, token):
        try:
            normalized = str(uuid.UUID(token))
        except (ValueError, TypeError, AttributeError) as error:
            raise FirmwareError("invalid-staging-token", "Invalid staging token") from error
        path = self.staging_dir / normalized
        metadata_path = self.staging_dir / f"{normalized}.json"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise FirmwareError("staging-not-found", "Staged firmware was not found") from error
        return normalized, path, metadata_path, metadata

    def list(self):
        if not self.staging_dir.is_dir():
            return []
        entries = []
        for metadata_path in sorted(self.staging_dir.glob("*.json")):
            try:
                entries.append(json.loads(metadata_path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return entries

    def claim(self, token, task_id):
        normalized, path, metadata_path, metadata = self._metadata(token)
        if not path.is_file():
            raise FirmwareError("staging-not-found", "Staged firmware was not found")
        owner = metadata.get("claimed_by_task")
        if owner and owner != task_id:
            raise FirmwareError("staging-in-use", "Staged firmware is in use")
        metadata["claimed_by_task"] = task_id
        metadata["last_used_at"] = time.time()
        self._write_metadata(metadata_path, metadata)
        return normalized

    def release(self, token, task_id=None):
        try:
            _, _, metadata_path, metadata = self._metadata(token)
        except FirmwareError:
            return
        if task_id is None or metadata.get("claimed_by_task") == task_id:
            metadata["claimed_by_task"] = None
            metadata["last_used_at"] = time.time()
            self._write_metadata(metadata_path, metadata)

    def consume(self, token, task_id=None):
        _, path, metadata_path, metadata = self._metadata(token)
        if metadata.get("claimed_by_task") not in (None, task_id):
            raise FirmwareError("staging-in-use", "Staged firmware is in use")
        path.unlink(missing_ok=True)
        metadata_path.unlink(missing_ok=True)

    def delete(self, token):
        normalized, path, metadata_path, metadata = self._metadata(token)
        if metadata.get("claimed_by_task"):
            raise FirmwareError("staging-in-use", "Staged firmware is in use")
        path.unlink(missing_ok=True)
        metadata_path.unlink(missing_ok=True)
        return normalized

    def gc(self, older_than_seconds=86400):
        cutoff = time.time() - max(0, int(older_than_seconds))
        deleted = []
        for metadata in self.list():
            if metadata.get("claimed_by_task"):
                continue
            last_used = metadata.get("last_used_at", metadata.get("created_at", 0))
            if last_used > cutoff:
                continue
            try:
                deleted.append(self.delete(metadata["token"]))
            except FirmwareError:
                continue
        return deleted

    def release_claims_for_task(self, task_id):
        for metadata in self.list():
            if metadata.get("claimed_by_task") == task_id:
                self.release(metadata["token"], task_id)

class FirmwareTaskCore:
    def __init__(self, registry=None, task_store=None, task_runner=None,
                 staging_store=None):
        self.registry = registry or BackendRegistry()
        self.task_store = task_store or TaskStore()
        self.staging_store = staging_store or StagingStore()
        for backend in self.registry.backends.values():
            bind = getattr(backend, "bind_staging_store", None)
            if bind is not None:
                bind(self.staging_store)
        self.task_runner = task_runner

    @staticmethod
    @contextlib.contextmanager
    def _admission_lock(blocking=False):
        path = Path(TASK_ADMISSION_LOCK)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            try:
                flags = fcntl.LOCK_EX
                if not blocking:
                    flags |= fcntl.LOCK_NB
                fcntl.flock(descriptor, flags)
            except BlockingIOError as error:
                raise FirmwareError(
                    "firmware-busy", "Another firmware operation is starting"
                ) from error
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    @staticmethod
    def _worker_unit(task_id):
        return TASK_UNIT.format(str(uuid.UUID(task_id)))

    @classmethod
    def _worker_active(cls, task_id):
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", cls._worker_unit(task_id)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0

    def _reconcile_running_tasks(self):
        for task in self.task_store.list():
            if task.get("state") != "running":
                continue
            if self._worker_active(task["id"]):
                continue
            task["state"] = "failed"
            task["phase"] = "interrupted"
            task["error"] = {
                "code": "worker-interrupted",
                "message": "Firmware worker stopped before the task completed",
            }
            self.task_store.write(task)
            for token in task.get("staging_tokens", []):
                self.staging_store.release(token, task["id"])

    @staticmethod
    def _staging_tokens(payload):
        if not isinstance(payload, dict):
            return []
        tokens = []
        for key, value in payload.items():
            if (key == "token" or key.startswith("firmware_")) and isinstance(value, str):
                tokens.append(value)
            elif isinstance(value, dict):
                tokens.extend(FirmwareTaskCore._staging_tokens(value))
        return list(dict.fromkeys(tokens))

    def _start_task(self, backend_name, payload, operation):
        backend = self.registry.get(backend_name)
        method_name = "rollback" if operation == "rollback" else "start"
        if not hasattr(backend, method_name):
            raise FirmwareError(
                "operation-unsupported",
                f"Backend '{backend_name}' does not support {operation}",
            )

        task_id = str(uuid.uuid4())
        staging_tokens = self._staging_tokens(payload)
        with self._admission_lock():
            self._reconcile_running_tasks()
            if any(task.get("state") == "running" for task in self.task_store.list()):
                raise FirmwareError(
                    "firmware-busy", "Another firmware operation is running")

            claimed_tokens = []
            task = None
            try:
                for token in staging_tokens:
                    self.staging_store.claim(token, task_id)
                    claimed_tokens.append(token)
                task = {
                    "id": task_id,
                    "backend": backend_name,
                    "operation": operation,
                    "payload": payload,
                    "state": "running",
                    "phase": "starting",
                    "result": None,
                    "error": None,
                    "staging_tokens": staging_tokens,
                }
                self.task_store.write(task)
                subprocess.run(
                    ["systemctl", "start", self._worker_unit(task_id)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30,
                )
            except (OSError, subprocess.CalledProcessError,
                    subprocess.TimeoutExpired) as error:
                if task is not None:
                    task["state"] = "failed"
                    task["phase"] = "failed"
                    task["error"] = {
                        "code": "worker-start-failed",
                        "message": "Firmware worker could not be started",
                    }
                    self.task_store.write(task)
                for token in claimed_tokens:
                    self.staging_store.release(token, task_id)
                raise FirmwareError(
                    "worker-start-failed",
                    "Firmware worker could not be started",
                ) from error
            except Exception:
                for token in claimed_tokens:
                    self.staging_store.release(token, task_id)
                raise
        return task

    def execute_task(self, task_id):
        task = self.task_store.read(task_id)
        if task.get("state") != "running":
            return task

        def progress(phase):
            task["phase"] = phase
            try:
                self.task_store.write(task)
            except OSError:
                pass

        try:
            backend = self.registry.get(task["backend"])
            method_name = (
                "rollback" if task.get("operation") == "rollback" else "start"
            )
            task["result"] = getattr(backend, method_name)(
                task.get("payload", {}), progress, self.staging_store)
            task["state"] = "succeeded"
            task["phase"] = "succeeded"
        except Exception as error:
            task["state"] = "failed"
            task["phase"] = "failed"
            if isinstance(error, FirmwareError):
                task["error"] = {
                    "code": error.code,
                    "message": error.message,
                }
                if error.details is not None:
                    task["error"]["details"] = error.details
            else:
                task["error"] = {
                    "code": "backend-failed",
                    "message": "Firmware operation failed",
                }
        finally:
            try:
                self.task_store.write(task)
            except OSError:
                pass
            for token in task.get("staging_tokens", []):
                try:
                    if task["state"] == "succeeded":
                        self.staging_store.consume(token, task["id"])
                    else:
                        self.staging_store.release(token, task["id"])
                except FirmwareError:
                    pass
        return task

    def handle(self, request):
        request_id = request.get("id")
        try:
            if request.get("v") != PROTOCOL_VERSION:
                raise FirmwareError(
                    "unsupported-version",
                    f"Only protocol version {PROTOCOL_VERSION} is supported",
                )
            operation = request.get("op")
            payload = request.get("payload", {})
            if not isinstance(payload, dict):
                raise FirmwareError("invalid-request", "payload must be an object")

            if operation == "capabilities.list":
                data = self.registry.capabilities()
            elif operation == "inspect.get":
                backend_name = request.get("backend")
                if not backend_name:
                    raise FirmwareError(
                        "invalid-request", "inspect.get requires a backend")
                backend = self.registry.get(backend_name)
                if payload.get("operation") == "rollback":
                    inspect = getattr(backend, "inspect_rollback", None)
                    if inspect is None:
                        raise FirmwareError(
                            "operation-unsupported",
                            f"Backend '{backend_name}' does not support rollback",
                        )
                    data = inspect(payload)
                else:
                    data = backend.inspect(payload)
            elif operation == "staging.import":
                source_path = payload.get("path")
                if not source_path:
                    raise FirmwareError(
                        "invalid-request", "staging.import requires a path")
                data = self.staging_store.import_file(
                    source_path, payload.get("name"))
            elif operation == "action.start":
                backend_name = request.get("backend")
                if not backend_name:
                    raise FirmwareError(
                        "invalid-request", "action.start requires a backend")
                data = self._start_task(backend_name, payload, "update")
            elif operation == "action.rollback":
                backend_name = request.get("backend")
                if not backend_name:
                    raise FirmwareError(
                        "invalid-request", "action.rollback requires a backend")
                data = self._start_task(backend_name, payload, "rollback")
            elif operation == "task.get":
                task_id = payload.get("task_id")
                if not task_id:
                    raise FirmwareError(
                        "invalid-request", "task.get requires a task_id")
                with self._admission_lock(blocking=True):
                    self._reconcile_running_tasks()
                data = self.task_store.read(task_id)
            elif operation == "staging.list":
                data = self.staging_store.list()
            elif operation == "staging.delete":
                token = payload.get("token")
                if not token:
                    raise FirmwareError(
                        "invalid-request", "staging.delete requires a token")
                data = {"token": self.staging_store.delete(token)}
            elif operation == "staging.gc":
                data = {
                    "deleted": self.staging_store.gc(
                        payload.get("older_than_seconds", 86400))
                }
            else:
                raise FirmwareError(
                    "unknown-operation", f"Unknown operation '{operation}'")

            return {
                "v": PROTOCOL_VERSION,
                "id": request_id,
                "ok": True,
                "data": data,
            }
        except FirmwareError as error:
            return {
                "v": PROTOCOL_VERSION,
                "id": request_id,
                "ok": False,
                "error": {
                    "code": error.code,
                    "message": error.message,
                },
            }
        except Exception:
            return {
                "v": PROTOCOL_VERSION,
                "id": request_id,
                "ok": False,
                "error": {
                    "code": "internal-error",
                    "message": "Internal firmware task error",
                },
            }


def decode_request(line):
    try:
        request = json.loads(line)
    except (TypeError, ValueError) as error:
        raise FirmwareError("invalid-json", "Request is not valid JSON") from error
    if not isinstance(request, dict):
        raise FirmwareError("invalid-request", "Request must be an object")
    return request


def encode_response(response):
    return json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n"
