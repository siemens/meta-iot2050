# Copyright (c) Siemens AG, 2026
# SPDX-License-Identifier: MIT
"""Root-only management and PAM operations on the private Node-RED store.

No system PAM/NSS files are copied. Password hashing/history/quality and
lockouts are implemented by Debian PAM modules, not by this management layer.
"""

import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import resource
import shutil
import stat
import subprocess
import sys
import tempfile


STATE = Path("/var/lib/iot2050-node-red-auth")
HELPER = Path("/usr/lib/iot2050/node-red-auth/pam-helper")
POLICY = Path("/etc/iot2050/node-red-auth/policy.json")
MAX_REQUEST = 16384
MAX_ACCOUNTS = 256

# When changing these limits, update the matching constants in pam-helper.c.
MAX_USERNAME_LENGTH = 32
MAX_PASSWORD_BYTES = 512  # Linux-PAM's PAM_MAX_RESP_SIZE
MIN_PRIVATE_UID = 15000
MAX_PRIVATE_UID = 60000

MIN_PRIVATE_GID = 15000
MAX_PRIVATE_GID = 60000
USER_PATTERN = re.compile(rf"[a-z_][a-z0-9_-]{{0,{MAX_USERNAME_LENGTH - 1}}}\Z")
POLICY_RANGES = {
    "minlen": (12, 128), "minclass": (3, 4), "maxrepeat": (1, 10),
    "maxsequence": (1, 10), "remember": (1, 400), "deny": (1, 100),
    "fail_interval": (1, 86400), "unlock_time": (1, 86400), "maxdays": (1, 3650),
}


class AuthError(Exception):
    """A safe error message, without passwords or raw PAM/tool output."""


class PublishedWriteError(OSError):
    """The replacement is visible, but its directory sync failed."""


def username(value):
    if not isinstance(value, str) or not USER_PATTERN.fullmatch(value):
        raise AuthError("Invalid Node-RED account name")
    if value in {"root", "nodered"}:
        raise AuthError("Reserved Node-RED account name")
    return value


def password(value):
    if not isinstance(value, str) or not value or len(value.encode()) > MAX_PASSWORD_BYTES:
        raise AuthError(f"Password must contain 1–{MAX_PASSWORD_BYTES} UTF-8 bytes")
    if any(character in value for character in "\x00\r\n"):
        raise AuthError("Password cannot contain NUL or newline characters")
    return value


def secure_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
        raise AuthError("Unsafe authentication file ownership or permissions")


def ensure_directory(path, mode=0o755):
    if not path.exists():
        path.mkdir(mode=mode)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
        raise AuthError("Unsafe authentication directory")


def read_json(path):
    secure_file(path)
    if path.stat().st_size > 65536:
        raise AuthError("Authentication configuration is too large")
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise AuthError("Invalid authentication configuration")
    return value


def atomic_write(path, content, mode=0o600, *, gid=None):
    ensure_directory(path.parent)
    fd, name = tempfile.mkstemp(prefix=".node-red-auth-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w") as output:
            if gid is not None:
                os.fchown(output.fileno(), 0, gid)
            os.fchmod(output.fileno(), mode)
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        try:
            directory = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError as error:
            raise PublishedWriteError(f"Cannot sync published file: {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def command(arguments, input_text=None):
    return subprocess.run(
        arguments, input=input_text, capture_output=True, text=True,
        timeout=15, check=False, close_fds=True,
        env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LC_ALL": "C"},
    )


def module(name):
    paths = list(Path("/usr/lib").glob(f"*/security/{name}.so"))
    if len(paths) != 1:
        raise AuthError("Required PAM module is unavailable")
    secure_file(paths[0].resolve())
    return paths[0]


class Backend:
    def __init__(self, state=STATE, helper=HELPER, policy_file=POLICY):
        self.state = state
        self.root = state / "root"
        self.helper = helper
        self.policy_file = policy_file

    @contextmanager
    def locked(self, exclusive=False):
        if os.geteuid() != 0:
            raise AuthError("Authentication management requires root")
        self.state.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = self.state.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
            raise AuthError("Unsafe authentication state directory")
        fd = os.open(self.state / ".lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            lock_info = os.fstat(fd)
            if not stat.S_ISREG(lock_info.st_mode) or lock_info.st_uid != 0 or lock_info.st_mode & 0o022:
                raise AuthError("Unsafe authentication lock")
            fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            yield
        finally:
            os.close(fd)

    def policy(self):
        values = read_json(self.policy_file)
        if set(values) != set(POLICY_RANGES):
            raise AuthError("Invalid password policy fields")
        for name, (minimum, maximum) in POLICY_RANGES.items():
            value = values[name]
            if type(value) is not int or not minimum <= value <= maximum:
                raise AuthError(f"Invalid password policy: {name}")
        return values

    def users(self):
        values = read_json(self.state / "users.json")
        version = values.get("version")
        if set(values) != {"version", "users"} or type(version) is not int or version != 1:
            raise AuthError("Invalid account configuration")
        users = values["users"]
        if not isinstance(users, dict) or len(users) > MAX_ACCOUNTS:
            raise AuthError("Invalid account configuration")
        for name, user in users.items():
            username(name)
            if not isinstance(user, dict) or set(user) != {"permissions", "http", "enabled"}:
                raise AuthError("Invalid account permissions")
            if (user["permissions"] not in ("*", "read") or
                    type(user["http"]) is not bool or type(user["enabled"]) is not bool):
                raise AuthError("Invalid account permissions")
        return users

    def save_users(self, users):
        atomic_write(self.state / "users.json", json.dumps({"version": 1, "users": users}) + "\n")

    def private_root(self):
        info = self.root.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
            raise AuthError("Unsafe private authentication root")
        ensure_directory(self.root / "etc")
        ensure_directory(self.root / "etc/pam.d")
        for name in ("passwd", "shadow", "group", "gshadow", "nsswitch.conf", "login.defs", "pam.d/node-red"):
            secure_file(self.root / "etc" / name)

    def _runtime_target(self, source):
        relative = source.relative_to("/")
        parent = self.root
        for part in relative.parts[:-1]:
            parent /= part
            ensure_directory(parent)
        return self.root / relative

    def copy_runtime(self, source, copied):
        if source in copied:
            return
        copied.add(source)
        secure_file(source.resolve())
        target = self._runtime_target(source)
        fd, name = tempfile.mkstemp(prefix=".runtime-", dir=target.parent)
        os.close(fd)
        try:
            shutil.copyfile(source, name)
            os.chmod(name, stat.S_IMODE(source.stat().st_mode) & ~0o6000)
            os.replace(name, target)
        finally:
            Path(name).unlink(missing_ok=True)
        result = command(["/usr/bin/ldd", str(source)])
        if result.returncode:
            raise AuthError("Cannot resolve authentication runtime dependencies")
        for dependency in re.findall(r"(?:=>\s+)?(/[^\s]+)", result.stdout):
            self.copy_runtime(Path(dependency), copied)

    def initialize(self):
        with self.locked(exclusive=True):
            policy = self.policy()
            established = (self.state / "users.json").exists()
            self._prepare_store(established)
            modules = self._refresh_runtime()
            self._write_pam_config(modules, policy)
            if not established:
                self.save_users({})

    def _prepare_store(self, established):
        self.root.mkdir(mode=0o700, exist_ok=True)
        info = self.root.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
            raise AuthError("Unsafe private authentication root")
        for directory in ("etc", "etc/pam.d", "etc/security", "etc/default", "var", "var/lib", "var/lib/faillock", "dev"):
            ensure_directory(self.root / directory)
        initial = {
            "etc/passwd": "root:x:0:0:root:/root:/usr/sbin/nologin\n",
            "etc/shadow": "root:!:0:0:99999:7:::\n",
            "etc/group": "root:x:0:\n", "etc/gshadow": "root:!::\n",
        }
        if established:
            self.users()
        for relative, content in initial.items():
            path = self.root / relative
            # Never recreate missing credential files for an established store.
            if not established and not path.exists():
                atomic_write(path, content)
            secure_file(path)
        atomic_write(self.root / "etc/nsswitch.conf", "passwd: files\ngroup: files\nshadow: files\ngshadow: files\n")
        atomic_write(
            self.root / "etc/login.defs",
            f"UID_MIN {MIN_PRIVATE_UID}\nUID_MAX {MAX_PRIVATE_UID}\n"
            f"GID_MIN {MIN_PRIVATE_GID}\nGID_MAX {MAX_PRIVATE_GID}\n"
            "CREATE_HOME no\nUSERGROUPS_ENAB yes\n",
        )

    def _refresh_runtime(self):
        modules = {name: module(name) for name in (
            "pam_unix", "pam_deny", "pam_faillock", "pam_pwquality", "pam_pwhistory",
            "pam_rootok", "pam_permit",
        )}
        copied = set()
        for source in (*modules.values(), Path("/usr/sbin/unix_chkpwd"), Path("/usr/sbin/unix_update"),
                       Path("/usr/sbin/pwhistory_helper"), Path("/usr/sbin/faillock")):
            self.copy_runtime(source, copied)
        for extension in ("hwm", "pwd", "pwi"):
            source = Path(f"/var/cache/cracklib/cracklib_dict.{extension}")
            secure_file(source)
            shutil.copy2(source, self._runtime_target(source))
        null = self.root / "dev/null"
        if not null.exists():
            os.mknod(null, stat.S_IFCHR | 0o666, os.makedev(1, 3))
        if not stat.S_ISCHR(null.lstat().st_mode) or null.stat().st_rdev != os.makedev(1, 3):
            raise AuthError("Invalid private null device")
        return modules

    def _write_pam_config(self, modules, policy):
        lockout = " ".join(f"{name}={policy[name]}" for name in ("deny", "fail_interval", "unlock_time"))
        lockout += " dir=/var/lib/faillock"
        quality = " ".join(f"{name}={policy[name]}" for name in ("minlen", "minclass", "maxrepeat", "maxsequence"))
        pam = (
            f"auth requisite {modules['pam_faillock']} preauth silent {lockout}\n"
            f"auth [success=1 default=bad] {modules['pam_unix']} nodelay\n"
            f"auth [default=die] {modules['pam_faillock']} authfail {lockout}\n"
            f"auth sufficient {modules['pam_faillock']} authsucc {lockout}\n"
            f"auth required {modules['pam_deny']}\n"
            f"account required {modules['pam_unix']}\n"
            f"password requisite {modules['pam_pwquality']} retry=1 {quality} dictcheck=1 enforce_for_root\n"
            f"password requisite {modules['pam_pwhistory']} remember={policy['remember']} use_authtok enforce_for_root\n"
            f"password required {modules['pam_unix']} use_authtok yescrypt\n"
        )
        atomic_write(self.root / "etc/pam.d/node-red", pam)
        # Shadow tools consult their own PAM services inside --root.
        # These stacks permit only the root-only management process, never
        # a Node-RED login. Password updates still use the node-red stack.
        administration = (
            f"auth required {modules['pam_rootok']}\n"
            f"account required {modules['pam_permit']}\n"
            f"session required {modules['pam_permit']}\n"
        )
        for service in ("useradd", "usermod", "userdel", "chage"):
            atomic_write(self.root / f"etc/pam.d/{service}", administration)

    def _run_pam(self, operation, name, secret=None):
        """Invoke the worker with credentials validated by the caller."""
        secure_file(self.helper)
        input_text = secret + "\n" if secret is not None else None
        result = command([str(self.helper), operation, name], input_text)
        try:
            value = json.loads(result.stdout)
        except ValueError as error:
            raise AuthError("Authentication worker failed") from error
        if not isinstance(value, dict) or type(value.get("status")) is not int:
            raise AuthError("Authentication worker failed")
        return result.returncode == 0 and value["status"] == 0

    def lookup(self, name, secret=None, http=False):
        name = username(name)
        if secret is not None:
            secret = password(secret)
        with self.locked():
            self.private_root()
            user = self.users().get(name)
            if not user or not user["enabled"] or (http and not user["http"]):
                return None
            operation = "authenticate" if secret is not None else "account"
            if not self._run_pam(operation, name, secret):
                return None
            return {"username": name, "permissions": user["permissions"]}

    def create(self, name, secret, permissions="*", http=True):
        name, secret = username(name), password(secret)
        if permissions not in ("*", "read") or type(http) is not bool:
            raise AuthError("Invalid account permissions")
        with self.locked(exclusive=True):
            self.private_root()
            users = self.users()
            passwd = self.root / "etc/passwd"
            if name in users or any(line.split(":")[0] == name for line in passwd.read_text().splitlines()):
                raise AuthError("Node-RED account already exists")
            if len(users) >= MAX_ACCOUNTS:
                raise AuthError("Node-RED account limit reached")
            result = command(["/usr/sbin/useradd", "--root", str(self.root), "--no-create-home",
                              "--user-group", "--shell", "/usr/sbin/nologin", name])
            if result.returncode:
                raise AuthError("Cannot create private Node-RED account")
            try:
                if not self._run_pam("change", name, secret):
                    raise AuthError("Password rejected by the Node-RED PAM policy")
                age = command(["/usr/bin/chage", "--root", str(self.root), "--maxdays", str(self.policy()["maxdays"]), name])
                if age.returncode:
                    raise AuthError("Cannot apply password ageing policy")
                users[name] = {"permissions": permissions, "http": http, "enabled": True}
                self.save_users(users)
            except PublishedWriteError:
                # The visible metadata already references this account.
                raise
            except Exception:
                command(["/usr/sbin/userdel", "--root", str(self.root), name])
                raise

    def manage(self, operation, name, secret=None):
        name = username(name)
        if operation not in {"reset", "disable", "enable", "unlock"}:
            raise AuthError("Invalid account management operation")
        with self.locked(exclusive=True):
            self.private_root()
            users = self.users()
            if name not in users:
                raise AuthError("Unknown Node-RED account")
            if operation == "reset":
                if not self._run_pam("change", name, password(secret)):
                    raise AuthError("Password rejected by the Node-RED PAM policy")
                if not users[name]["enabled"]:
                    operation = "disable"
            if operation in {"disable", "enable"}:
                option = "--lock" if operation == "disable" else "--unlock"
                result = command(["/usr/sbin/usermod", "--root", str(self.root), option, name])
                if result.returncode:
                    raise AuthError("Cannot change private account state")
                users[name]["enabled"] = operation == "enable"
                self.save_users(users)
            if operation == "unlock":
                result = command(["/usr/sbin/chroot", str(self.root), "/usr/sbin/faillock",
                                  "--dir", "/var/lib/faillock", "--user", name, "--reset"])
                if result.returncode:
                    raise AuthError("Cannot unlock private account")


def main():
    parser = argparse.ArgumentParser(description="Root-only Node-RED private account management")
    parser.add_argument("operation", choices=("initialize", "create", "reset", "disable", "enable", "unlock"))
    arguments = parser.parse_args()
    try:
        if os.getuid() != 0 or os.geteuid() != 0:
            raise AuthError("Node-RED account management requires root")
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        backend = Backend()
        if arguments.operation == "initialize":
            backend.initialize()
        else:
            raw = sys.stdin.buffer.read(MAX_REQUEST + 1)
            if len(raw) > MAX_REQUEST:
                raise AuthError("Account request is too large")
            request = json.loads(raw)
            if not isinstance(request, dict):
                raise AuthError("Invalid account request")
            allowed = {"username", "password", "permissions", "http"} if arguments.operation == "create" else {"username", "password"}
            if set(request) - allowed:
                raise AuthError("Unsupported account request fields")
            if arguments.operation == "create":
                backend.create(request.get("username"), request.get("password"),
                               request.get("permissions", "*"), request.get("http", True))
            else:
                backend.manage(arguments.operation, request.get("username"), request.get("password"))
        print(json.dumps({"ok": True}))
        return 0
    except (AuthError, OSError, ValueError, subprocess.SubprocessError):
        print(json.dumps({"ok": False, "error": "Node-RED account operation failed"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
