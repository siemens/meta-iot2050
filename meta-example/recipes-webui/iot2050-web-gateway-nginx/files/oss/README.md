# OSS Clearing archive

The `ReadmeOSS-All_in_One.zip` archive is an optional build input. It is not
stored in Git because the release-specific archive is supplied separately.

Before building, copy the archive into this directory with the exact name:

```text
ReadmeOSS-All_in_One.zip
```

The archive can be provided locally or copied here by the pipeline before the
build starts.

If the archive is not supplied, the gateway recipe still builds normally, but
the `/oss` download is unavailable in the resulting image.