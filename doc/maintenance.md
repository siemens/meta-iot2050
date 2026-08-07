# Maintenance & Firmware Operations

> TL;DR: Flash `.wic` (prefer `bmaptool`), configure or note default
> networking, optionally install to eMMC via USER button, update firmware with
> `iot2050-firmware-update`, and adapt/restore the U-Boot environment as needed.

## Flashing Images
There are two primary methods for flashing the `.wic` image file to an SD card or
other storages.

### Using `bmaptool` (Recommended)
For the fastest and safest flashing, use `bmaptool`. This tool provides
better performance and verifies the written data.
```sh
sudo bmaptool copy <image>.wic /dev/mmcblk0
```

### Using `dd`
Alternatively, you can use the standard `dd` utility. This method is
more basic but universally available.
```sh
sudo dd if=<image>.wic of=/dev/mmcblk0 bs=4M oflag=sync status=progress
```

## Boot Networking
- **Example image**: static `192.168.200.1` on the first Ethernet port + DHCP
  on the second interface.
- **Base BSP image**: no network preconfigured (must be configured manually
  via the UART console).

## Login Security Operations

For package architecture and implementation details, see
[`meta/recipes-core/iot2050-login-security/README.md`](../meta/recipes-core/iot2050-login-security/README.md).
For repository validation commands, see
[`scripts/host/README.md`](../scripts/host/README.md).

**Credentials (Example image default)**: no preset `root` password is shipped.
First-boot onboarding creates the named administrator account, while the root
password remains locked and direct root SSH login is disabled.

**Development compatibility**: when explicitly built with
`kas-iot2050-example.yml:kas/opt/dev.yml`, the image restores legacy `root`
and `iot2050` credentials with forced password change and direct root SSH for
local development workflows.

The Dev SSH compatibility package removes the Example image `PermitRootLogin no`
drop-in before installing its later `PermitRootLogin yes` compatibility rule.
This is intentionally limited to the explicit Dev append and is not present in
Example images.

**Failed-login security baseline**: password-based authentication currently
ships with `deny=5`, `fail_interval=900`, `unlock_time=900`,
`even_deny_root`, and `root_unlock_time=900`. An administrator can clear a
lockout by resetting the failed-attempt state on the device.

Failed-login counters are stored under `/var/lib/faillock` so they survive
service restart and reboot. Runtime validation should verify this persistence.

Named-account passwords use the system `pam_pwquality` policy. The baseline
requires at least 12 characters and at least 3 of 4 character classes
(lowercase, uppercase, digits, and symbols), and rejects long repeated runs
and simple numeric sequences. This policy is applied by PAM so
it covers the onboarding `chpasswd` path, interactive `passwd`, and the
privileged backend password-reset path consistently. The image also installs
the CrackLib runtime and an explicit wordlist so dictionary checks work during
password changes.

To inspect or clear the failed-login state of a named account on the device:
```sh
sudo iot2050-failed-login status <user>
sudo iot2050-failed-login reset <user>
```

To reset a named user's password locally and clear its failed-login state in
one step:
```sh
sudo iot2050-account-admin set-password <user>
```

To clear a named user's failed-login state through the account helper:
```sh
sudo iot2050-account-admin unlock <user>
```

For account lifecycle operations, use the privileged backend:
```sh
sudo iot2050-login-backend account status <user>
sudo iot2050-login-backend account disable <user>
sudo iot2050-login-backend account enable <user>
sudo iot2050-login-backend account delete <user>
```

The backend only permits named interactive accounts and protects the last
usable `iot2050-admin` administrator.

For target-device runtime validation, run the remote checker from the
repository root. The default mode prompts for the SSH and sudo passwords
without echoing them:
```sh
bash scripts/host/check-login-runtime-remote.sh
```

The checker validates the `iot2050-admin` group, backend socket and service
state, effective `PermitRootLogin`, persistent faillock storage, and a backend
smoke response. It prints colored `INFO`, `PASS`, and `FAIL` markers on an
interactive terminal; set `NO_COLOR=1` for plain output.

For automation or a lab-only device, a direct password argument is also
supported. Quote the value when needed, and remember that command-line
passwords can be recorded in shell history or process listings:
```sh
bash scripts/host/check-login-runtime-remote.sh --password 'password'
```

To include a read-only account lifecycle probe, provide an existing named
account. This only calls `account status`; it does not create, disable, enable,
or delete any account:
```sh
bash scripts/host/check-login-runtime-remote.sh --lifecycle-user iot2050
```

The probe passes when the backend returns `error_code=OK` for the requested
account. Use a named test account on a development image when validating the
full lifecycle operations separately; do not use the only administrator for
destructive tests.

For a complete, destructive lifecycle integration test, provide a temporary
account name with the required `iot2050-rt-` prefix. The checker creates the
account, exercises disable/enable/status/delete, and removes it automatically
on failure:
```sh
bash scripts/host/check-login-runtime-remote.sh \
  --lifecycle-test-user iot2050-rt-a
```

This mode must only be used on a test device. It never accepts an arbitrary
account name, which prevents accidental operations on a real administrator.

## eMMC Installation
This installation flow is provided by the example image. It is not available
in the base/minimal image or the SWUpdate image variants.

On the very first boot from an SD card or USB stick, you can trigger an
installation to the internal eMMC. Hold the **USER button** while the status
LED blinks orange (this is the first-boot window) for at least 5 seconds to
begin.

**LED states** (during installation phase):
- Slow orange blink: First-boot window (you can trigger the install now).
- Fast blink: eMMC copy is in progress (do **NOT** power off).
- Solid / reboot: Install finished (the device will reboot automatically).

**WARNING**: All existing eMMC content will be overwritten.

To trigger this automatically, create a flag file before booting:
```sh
touch <mountpoint>/etc/install-on-emmc
```

For the example image, `<mountpoint>` must be the Linux rootfs partition
(label `rootfs`). Do not place the file on the EFI partition or on the `BOOT`
partition.

## Firmware Update Tool
To apply a firmware update package from the running system:
```sh
iot2050-firmware-update /usr/share/iot2050/fwu/IOT2050-FW-Update-PKG-<Version>.tar.xz
```

## Selecting Boot Device (Temporary Override)
In the U-Boot serial console, you can temporarily change the boot device:
```
=> setenv boot_targets mmc0
=> run bootcmd
```

## Restoring U-Boot Environment
To restore the bootloader environment to its default state:
```sh
fw_setenv -f /etc/u-boot-initial-env
```

### Automatic Environment Adaptation & Watchdog
During the very first boot after flashing, the `patch-u-boot-env.service`
adjusts the bootloader environment. This ensures the correct root filesystem
slot is selected and, for SWUpdate images, prepares A/B handling.

It also enables the hardware watchdog in U-Boot with a 60-second timeout by
default. This ensures that a hang during early userspace brings the system
back under watchdog control.

If you need to re-trigger that logic (e.g., after manual environment edits),
reset the environment (see above) and reboot; the service will run again if
its marker conditions are unmet.

**Note**: For SWUpdate (A/B) images, the adapted environment cooperates with
EFI Boot Guard to select the correct inactive slot and to arm rollback
protection until `complete_update.sh` marks the update as successful.

