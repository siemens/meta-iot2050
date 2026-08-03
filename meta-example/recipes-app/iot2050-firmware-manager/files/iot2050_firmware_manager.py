# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""Core protocol and provider registry for the IOT2050 firmware manager."""

import importlib.util
import hashlib
import json
import os
import stat
import sys
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


PROTOCOL_VERSION = 1
DEFAULT_PROVIDER_DIR = "/usr/lib/iot2050/firmware-manager/providers.d"
DEFAULT_TASK_DIR = "/var/lib/iot2050-fwmgr/tasks"
DEFAULT_STAGING_DIR = "/var/lib/iot2050-fwmgr/staging"
DEFAULT_SYSTEM_BACKUP_DIR = "/var/lib/iot2050-fwmgr/system-backup"
DEFAULT_MAX_FIRMWARE_SIZE = 64 * 1024 * 1024


class ManagerError(Exception):
    """A stable error returned through the manager IPC."""

    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


class SystemFirmwareProvider:
    name = "system"

    def __init__(self, backup_dir=DEFAULT_SYSTEM_BACKUP_DIR):
        self.backup_dir = Path(backup_dir)
        self.staging_store = None

    def bind_staging_store(self, staging_store):
        self.staging_store = staging_store

    def available(self):
        return True, None

    def capabilities(self):
        return {
            "provider": self.name,
            "label": "System Firmware",
            "operations": ["inspect", "update"],
            "source": "upload",
            "requires_signature": True,
        }

    def inspect(self, request):
        path, staging = self._resolve(request)
        try:
            from iot2050_firmware_update import inspect_system_firmware
            details = inspect_system_firmware(path)
        except ImportError as error:
            raise ManagerError(
                "system-updater-unavailable",
                "System firmware updater is unavailable",
            ) from error
        except Exception as error:
            self._raise_update_error(error)
        return {**details, "package": staging}

    def start(self, request, progress, staging_store):
        path, staging = self._resolve(request, staging_store)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.backup_dir, 0o700)
        try:
            from iot2050_firmware_update import update_system_firmware
            result = update_system_firmware(
                path,
                str(self.backup_dir),
                preserve_list=request.get("preserve_list"),
                reset=bool(request.get("reset", False)),
                progress=progress,
            )
        except ImportError as error:
            raise ManagerError(
                "system-updater-unavailable",
                "System firmware updater is unavailable",
            ) from error
        except Exception as error:
            self._raise_update_error(error)
        return {**result, "package": staging}

    def _resolve(self, request, staging_store=None):
        store = staging_store or self.staging_store
        token = request.get("token")
        if store is None or not token:
            raise ManagerError(
                "staging-required", "A staged system firmware package is required")
        return store.resolve(token)

    @staticmethod
    def _raise_update_error(error):
        # Keep updater internals and paths out of the IPC while preserving the
        # stable numeric code needed by support and existing CLI documentation.
        code = getattr(error, "code", None)
        if code is None:
            raise ManagerError(
                "system-update-failed", "System firmware operation failed"
            ) from error
        messages = {
            3: "System firmware backup failed",
            5: "System firmware flashing or readback failed",
            7: "The package is not valid for this device",
            9: "The firmware signature is missing",
            10: "The firmware verification key is unavailable",
            11: "The firmware signature is invalid",
        }
        raise ManagerError(
            "system-update-rejected",
            messages.get(code, "System firmware operation was rejected"),
            {"updater_code": code},
        ) from error


class ProviderRegistry:
    def __init__(self, provider_dir=DEFAULT_PROVIDER_DIR, builtins=None):
        self.provider_dir = Path(provider_dir)
        self.providers = {}
        self.discovery_errors = []
        for provider in builtins or [SystemFirmwareProvider()]:
            self.register(provider)

    def register(self, provider):
        name = getattr(provider, "name", None)
        if not name or not isinstance(name, str):
            raise ManagerError("invalid-provider", "Provider has no valid name")
        if name in self.providers:
            raise ManagerError(
                "duplicate-provider", f"Provider '{name}' is already registered")
        self.providers[name] = provider

    def discover(self):
        if not self.provider_dir.is_dir():
            return
        for descriptor_path in sorted(self.provider_dir.glob("*.json")):
            try:
                descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
                module_path = descriptor_path.parent / descriptor["module"]
                class_name = descriptor["class"]
                module_name = f"iot2050_firmware_provider_{descriptor_path.stem}"
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
                    f"Failed to load firmware provider {descriptor_path.name}: {error}",
                    file=sys.stderr,
                )

    def available_providers(self):
        available = {}
        for name, provider in self.providers.items():
            is_available, reason = provider.available()
            if is_available:
                available[name] = provider
            elif reason:
                continue
        return available

    def get(self, name):
        provider = self.available_providers().get(name)
        if provider is None:
            raise ManagerError(
                "provider-unavailable", f"Provider '{name}' is unavailable")
        return provider


class TaskStore:
    def __init__(self, task_dir=DEFAULT_TASK_DIR):
        self.task_dir = Path(task_dir)
        self._lock = threading.Lock()

    def _path(self, task_id):
        try:
            normalized = str(uuid.UUID(task_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise ManagerError("invalid-task", "Invalid task ID") from error
        return self.task_dir / f"{normalized}.json"

    def write(self, task):
        self.task_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.task_dir, 0o700)
        path = self._path(task["id"])
        temporary = path.with_suffix(".tmp")
        with self._lock:
            temporary.write_text(
                json.dumps(task, separators=(",", ":"), sort_keys=True),
                encoding="utf-8",
            )
            os.chmod(temporary, 0o600)
            os.replace(temporary, path)

    def read(self, task_id):
        path = self._path(task_id)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise ManagerError("task-not-found", "Task was not found") from error

    def reconcile_interrupted(self):
        if not self.task_dir.is_dir():
            return
        for path in self.task_dir.glob("*.json"):
            try:
                task = json.loads(path.read_text(encoding="utf-8"))
                if task.get("state") not in ("queued", "running"):
                    continue
                task["state"] = "failed"
                task["phase"] = "interrupted"
                task["error"] = {
                    "code": "manager-interrupted",
                    "message": "Firmware manager stopped before the task completed",
                }
                self.write(task)
            except (OSError, ValueError, ManagerError):
                continue


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
            raise ManagerError("source-unavailable", "Firmware file is unavailable") from error
        if not stat.S_ISREG(source_stat.st_mode):
            os.close(source_fd)
            raise ManagerError("invalid-source", "Firmware source is not a regular file")
        if source_stat.st_size > self.max_size:
            os.close(source_fd)
            raise ManagerError("firmware-too-large", "Firmware file exceeds the size limit")

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
                        raise ManagerError(
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
        }
        metadata_path = self.staging_dir / f"{token}.json"
        metadata_path.write_text(
            json.dumps(metadata, separators=(",", ":"), sort_keys=True),
            encoding="utf-8",
        )
        os.chmod(metadata_path, 0o600)
        return metadata

    def resolve(self, token):
        try:
            normalized = str(uuid.UUID(token))
        except (ValueError, TypeError, AttributeError) as error:
            raise ManagerError("invalid-staging-token", "Invalid staging token") from error
        path = self.staging_dir / normalized
        metadata_path = self.staging_dir / f"{normalized}.json"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise ManagerError("staging-not-found", "Staged firmware was not found") from error
        if not path.is_file():
            raise ManagerError("staging-not-found", "Staged firmware was not found")
        digest = hashlib.sha256()
        size = 0
        try:
            with path.open("rb") as staged_file:
                for chunk in iter(lambda: staged_file.read(1024 * 1024), b""):
                    size += len(chunk)
                    digest.update(chunk)
        except OSError as error:
            raise ManagerError(
                "staging-unavailable", "Staged firmware is unavailable") from error
        if size != metadata.get("size") or digest.hexdigest() != metadata.get("sha256"):
            raise ManagerError(
                "staging-integrity-failed", "Staged firmware integrity check failed")
        return path, metadata


class TaskRunner:
    def __init__(self, registry, store, staging_store, executor=None):
        self.registry = registry
        self.store = store
        self.staging_store = staging_store
        self.executor = executor or ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="firmware-update")
        self._hardware_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._active_task_id = None
        self._accepting = True

    def start(self, provider_name, payload):
        provider = self.registry.get(provider_name)
        if not hasattr(provider, "start"):
            raise ManagerError(
                "operation-unsupported",
                f"Provider '{provider_name}' does not support updates",
            )
        task_id = str(uuid.uuid4())
        with self._state_lock:
            if not self._accepting:
                raise ManagerError(
                    "manager-stopping", "Firmware manager is stopping")
            if self._active_task_id is not None:
                raise ManagerError(
                    "firmware-busy", "Another firmware operation is running")
            self._active_task_id = task_id

        task = {
            "id": task_id,
            "provider": provider_name,
            "state": "queued",
            "phase": "queued",
            "result": None,
            "error": None,
        }
        try:
            self.store.write(task)
            self.executor.submit(self._run, task, provider, payload)
        except Exception:
            with self._state_lock:
                self._active_task_id = None
            raise
        return task

    def _run(self, task, provider, payload):
        with self._hardware_lock:
            task["state"] = "running"
            task["phase"] = "flashing"
            self.store.write(task)

            def progress(phase):
                task["phase"] = phase
                self.store.write(task)

            try:
                task["result"] = provider.start(
                    payload, progress, self.staging_store)
                task["state"] = "succeeded"
                task["phase"] = "succeeded"
            except ManagerError as error:
                task["state"] = "failed"
                task["phase"] = "failed"
                task["error"] = {
                    "code": error.code,
                    "message": error.message,
                }
                if error.details is not None:
                    task["error"]["details"] = error.details
            except Exception:
                task["state"] = "failed"
                task["phase"] = "failed"
                task["error"] = {
                    "code": "provider-failed",
                    "message": "Firmware operation failed",
                }
            finally:
                self.store.write(task)
                with self._state_lock:
                    self._active_task_id = None

    def shutdown(self):
        self.stop_accepting()
        self.executor.shutdown(wait=True, cancel_futures=False)

    def stop_accepting(self):
        with self._state_lock:
            self._accepting = False


class FirmwareManager:
    def __init__(self, registry=None, task_store=None, task_runner=None,
                 staging_store=None):
        self.registry = registry or ProviderRegistry()
        self.task_store = task_store or TaskStore()
        self.task_store.reconcile_interrupted()
        self.staging_store = staging_store or StagingStore()
        for provider in self.registry.providers.values():
            bind = getattr(provider, "bind_staging_store", None)
            if bind is not None:
                bind(self.staging_store)
        self.task_runner = task_runner or TaskRunner(
            self.registry, self.task_store, self.staging_store)

    def handle(self, request):
        request_id = request.get("id")
        try:
            if request.get("v") != PROTOCOL_VERSION:
                raise ManagerError(
                    "unsupported-version",
                    f"Only protocol version {PROTOCOL_VERSION} is supported",
                )
            operation = request.get("op")
            payload = request.get("payload", {})
            if not isinstance(payload, dict):
                raise ManagerError("invalid-request", "payload must be an object")

            if operation == "capabilities.list":
                data = [
                    provider.capabilities()
                    for provider in self.registry.available_providers().values()
                ]
            elif operation == "inspect.get":
                provider_name = request.get("provider")
                if not provider_name:
                    raise ManagerError(
                        "invalid-request", "inspect.get requires a provider")
                data = self.registry.get(provider_name).inspect(payload)
            elif operation == "staging.import":
                source_path = payload.get("path")
                if not source_path:
                    raise ManagerError(
                        "invalid-request", "staging.import requires a path")
                data = self.staging_store.import_file(
                    source_path, payload.get("name"))
            elif operation == "action.start":
                provider_name = request.get("provider")
                if not provider_name:
                    raise ManagerError(
                        "invalid-request", "action.start requires a provider")
                data = self.task_runner.start(provider_name, payload)
            elif operation == "task.get":
                task_id = payload.get("task_id")
                if not task_id:
                    raise ManagerError(
                        "invalid-request", "task.get requires a task_id")
                data = self.task_store.read(task_id)
            else:
                raise ManagerError(
                    "unknown-operation", f"Unknown operation '{operation}'")

            return {
                "v": PROTOCOL_VERSION,
                "id": request_id,
                "ok": True,
                "data": data,
            }
        except ManagerError as error:
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
                    "message": "Internal firmware manager error",
                },
            }


def decode_request(line):
    try:
        request = json.loads(line)
    except (TypeError, ValueError) as error:
        raise ManagerError("invalid-json", "Request is not valid JSON") from error
    if not isinstance(request, dict):
        raise ManagerError("invalid-request", "Request must be an object")
    return request


def encode_response(response):
    return json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n"
