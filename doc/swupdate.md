# SWUpdate Image & Update Procedure
_Applies to version: v1.6.0+_

> TL;DR: Build the A/B image via `kas-iot2050-swupdate.yml`, flash the
> `.wic`, apply future updates with the `.swu`, then run
> `complete_update.sh` to confirm.

## 1. Building an SWUpdate Image

Build the dedicated SWUpdate image descriptor (already includes example
content, Node-RED, SM):
```
./kas-container build kas-iot2050-swupdate.yml
```

Resulting artifacts:
- `.wic` dual-rootfs image (A/B partitions)
- `.wic.bmap` (optional faster flashing)
- `.swu` update bundle for in-field updates

Typical deploy path:
```
build/tmp/deploy/images/iot2050/
```

## 2. Flashing for Initial Deployment

Flash the `.wic` to an SD card (example device `/dev/mmcblk0`):
```
sudo bmaptool copy iot2050-image-swu-example-*.wic /dev/mmcblk0
```
or use `dd` if `bmaptool` is unavailable.

## 3. Performing an Update

1. Copy the generated `.swu` file to the target.
2. Invoke SWUpdate:
```
swupdate -i iot2050-image-swu-example-*.swu
```
3. Reboot – system automatically switches to the inactive rootfs.
4. Validate functionality, then mark success:
```
complete_update.sh
```

If success is not confirmed (script not run) and a subsequent boot fails,
EFI Boot Guard falls back to the previous rootfs.

## 4. Notes

- A/B layout increases image size (dual rootfs) – plan for ~7 GB.
- `.swu` contains metadata directing which inactive slot to write.
- No web UI example is bundled by default.

## 5. Bootloader Environment Handling

The `patch-u-boot-env.service` updates environment variables and enables a
watchdog on first boot.

Reset to defaults when needed:
```
fw_setenv -f /etc/u-boot-initial-env
```

## 6. Troubleshooting

| Symptom | Hint |
|---------|------|
| Update reboots into old rootfs | `complete_update.sh` not run or watchdog reset | 
| SWUpdate aborts: missing handler | Ensure swupdate image used (correct descriptor) |
| Boot loop after update | Try booting old slot; inspect EFI Boot Guard variables |

## 7. Related
- [secure-boot](secure-boot.md) (combining Secure Boot + A/B)
- [maintenance](maintenance.md) (flashing, environment adaptation)

