# SWUpdate Image & Update Procedure
_Applies to version: v1.6.0+_

> TL;DR: Build the A/B image via `kas-iot2050-swupdate.yml`, flash the
> resulting `.wic` file, apply future updates using the `.swu` bundle, and
> then run `complete_update.sh` to confirm the update.

## Building an SWUpdate Image

Build the dedicated SWUpdate image descriptor, which already includes example
content, Node-RED, and SM variant support:
```sh
./kas-container build kas-iot2050-swupdate.yml
```

**Resulting artifacts**:
- `.wic`: A dual-rootfs image with A/B partitions for initial flashing.
- `.wic.bmap`: An optional map file for faster flashing with `bmaptool`.
- `.swu`: An update bundle for in-field updates.

The typical deployment path for these files is:
`build/tmp/deploy/images/iot2050/`

## Flashing for Initial Deployment

Flash the `.wic` file to an SD card. For example, using `/dev/mmcblk0`:
```sh
sudo bmaptool copy iot2050-image-swu-example-*.wic /dev/mmcblk0
```
You can use `dd` if `bmaptool` is unavailable, but it is slower and less safe.

## Performing an Update

1. Copy the generated `.swu` file to the target device.
2. Invoke SWUpdate to apply the bundle:
   ```sh
   swupdate -i iot2050-image-swu-example-*.swu
   ```
3. Reboot the device. The system will automatically switch to the newly
   updated (previously inactive) rootfs.
4. Validate that your application and system functionality are correct.
5. Mark the update as successful to make it permanent:
   ```sh
   complete_update.sh
   ```

If success is not confirmed (the script is not run) and a subsequent boot
fails, EFI Boot Guard will automatically fall back to the previous, working
rootfs.

## Notes

- The A/B layout increases the image size due to the dual rootfs partitions.
  Plan for a storage footprint of approximately 10 GB.
- The `.swu` bundle contains metadata that directs the update tool to write
  to the correct inactive slot.

## Bootloader Environment Handling

On the first boot, the `patch-u-boot-env.service` automatically updates
environment variables and enables a hardware watchdog.

You can reset the environment to its default state if needed:
```sh
fw_setenv -f /etc/u-boot-initial-env
```

