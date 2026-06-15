#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2026
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT

import grp
import json
import pwd
import re
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


STATE_DIR = Path('/var/lib/iot2050-firstboot-onboarding')
REQUEST_FILE = STATE_DIR / 'last-request.json'
DEFAULT_ADMIN_GROUPS = ('sudo', 'adm', 'dialout')
RESERVED_USERNAMES = {'root'}
USERNAME_PATTERN = re.compile(r'^[a-z_][a-z0-9_-]{0,31}$')
HOSTNAME_PATTERN = re.compile(r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$')


def run_command(arguments, input_text=None):
    return subprocess.run(
        arguments,
        input=input_text,
        capture_output=True,
        check=False,
        text=True,
    )


def existing_admin_groups():
    groups = []

    for group_name in DEFAULT_ADMIN_GROUPS:
        try:
            grp.getgrnam(group_name)
        except KeyError:
            continue
        groups.append(group_name)

    return groups


def update_hosts_file(current_hostname, new_hostname):
    hosts_path = Path('/etc/hosts')
    if hosts_path.exists():
        lines = hosts_path.read_text(encoding='utf-8').splitlines()
    else:
        lines = []

    updated_lines = []
    current_candidates = {current_hostname, new_hostname}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            updated_lines.append(line)
            continue

        fields = stripped.split()
        address = fields[0]
        aliases = fields[1:]

        if address == '127.0.0.1' and 'localhost' in aliases and current_candidates.intersection(aliases):
            updated_lines.append('127.0.0.1\tlocalhost')
            continue

        if address == '127.0.1.1':
            continue

        updated_lines.append(line)

    updated_lines.append(f'127.0.1.1\t{new_hostname}')
    hosts_path.write_text('\n'.join(updated_lines).rstrip() + '\n', encoding='utf-8')


def apply_hostname(device_name):
    if not device_name:
        return None, None

    normalized_name = device_name.lower()
    current_hostname = socket.gethostname()

    if normalized_name == current_hostname:
        return normalized_name, None

    if shutil.which('hostnamectl'):
        result = run_command(['hostnamectl', 'set-hostname', normalized_name])
    else:
        result = run_command(['hostname', normalized_name])

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        return None, message or 'Unable to update the device name.'

    Path('/etc/hostname').write_text(normalized_name + '\n', encoding='utf-8')
    update_hosts_file(current_hostname, normalized_name)
    return normalized_name, None


def create_user(username, password, full_name, admin_groups):
    user_shell = '/bin/bash' if Path('/bin/bash').exists() else '/bin/sh'
    command = [
        'useradd',
        '--create-home',
        '--user-group',
        '--shell', user_shell,
    ]

    if full_name:
        command.extend(['--comment', full_name])

    if admin_groups:
        command.extend(['--groups', ','.join(admin_groups)])

    command.append(username)

    result = run_command(command)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        return message or 'Unable to create the user account.'

    password_result = run_command(['chpasswd'], input_text=f'{username}:{password}\n')
    if password_result.returncode == 0:
        return None

    rollback = run_command(['userdel', '--remove', username])
    message = password_result.stderr.strip() or password_result.stdout.strip()
    if rollback.returncode != 0:
        rollback_message = rollback.stderr.strip() or rollback.stdout.strip()
        if rollback_message:
            message = f'{message} Rollback failed: {rollback_message}'.strip()

    return message or 'Unable to set the user password.'


def write_request_snapshot(payload, status, message, admin_groups, device_name):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    request_snapshot = {
        'submitted_at': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'message': message,
        'fullName': payload.get('fullName', ''),
        'username': payload.get('username', ''),
        'deviceName': device_name or payload.get('deviceName', ''),
        'grantAdmin': parse_bool(payload.get('grantAdmin', True), default=True),
        'adminGroups': admin_groups,
    }
    REQUEST_FILE.write_text(json.dumps(request_snapshot, indent=2), encoding='utf-8')
    REQUEST_FILE.chmod(0o600)


def helper_error(message, field_errors=None):
    return {
        'status': 'error',
        'message': message,
        'fieldErrors': field_errors or {},
    }


def validate_payload(username, full_name, password, confirm_password, device_name):
    errors = {}

    if not username:
        errors['username'] = 'Choose a user name.'
    elif username in RESERVED_USERNAMES:
        errors['username'] = 'The root account cannot be used for onboarding.'
    elif not USERNAME_PATTERN.fullmatch(username):
        errors['username'] = 'Use a Linux-compatible user name starting with a lowercase letter or underscore.'

    if not password:
        errors['password'] = 'Choose a password.'
    elif len(password) < 8:
        errors['password'] = 'Use at least 8 characters.'

    if confirm_password != password:
        errors['confirmPassword'] = 'Passwords do not match.'

    if full_name and len(full_name) > 64:
        errors['fullName'] = 'Keep the full name under 64 characters.'

    if device_name and (len(device_name) > 63 or not HOSTNAME_PATTERN.fullmatch(device_name)):
        errors['deviceName'] = 'Use letters, digits, or hyphens for the device name.'

    if errors:
        return helper_error('Please correct the highlighted fields.', errors)

    return None


def parse_bool(value, default=True):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ('1', 'true', 'yes', 'on'):
            return True
        if normalized in ('0', 'false', 'no', 'off'):
            return False
    return bool(value)


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps(helper_error('The onboarding request is not valid JSON.')))
        return

    username = str(payload.get('username', '')).strip()
    full_name = str(payload.get('fullName', '')).strip()
    password = str(payload.get('password', ''))
    confirm_password = str(payload.get('confirmPassword', ''))
    device_name = str(payload.get('deviceName', '')).strip()
    grant_admin = parse_bool(payload.get('grantAdmin', True), default=True)

    validation_error = validate_payload(username, full_name, password, confirm_password, device_name)
    if validation_error:
        write_request_snapshot(payload, validation_error['status'], validation_error['message'], [], device_name)
        print(json.dumps(validation_error))
        return

    try:
        pwd.getpwnam(username)
    except KeyError:
        pass
    else:
        result = helper_error('The selected user name already exists.', {
            'username': 'Choose another user name.'
        })
        write_request_snapshot(payload, result['status'], result['message'], [], device_name)
        print(json.dumps(result))
        return

    applied_device_name, hostname_error = apply_hostname(device_name)
    if hostname_error:
        result = helper_error(hostname_error, {
            'deviceName': 'Unable to apply the requested device name.'
        })
        write_request_snapshot(payload, result['status'], result['message'], [], device_name)
        print(json.dumps(result))
        return

    admin_groups = existing_admin_groups() if grant_admin else []
    user_error = create_user(username, password, full_name, admin_groups)
    if user_error:
        result = helper_error(user_error, {
            'username': 'Unable to create the requested user account.'
        })
        write_request_snapshot(payload, result['status'], result['message'], admin_groups, applied_device_name)
        print(json.dumps(result))
        return

    result = {
        'status': 'ok',
        'message': 'Administrator account created successfully.',
        'username': username,
        'deviceName': applied_device_name,
        'adminGroups': admin_groups,
    }
    write_request_snapshot(payload, result['status'], result['message'], admin_groups, applied_device_name)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
