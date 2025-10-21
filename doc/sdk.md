# SDK Usage
_Applies to version: v1.6.0+_

> TL;DR: Build with `:kas/opt/sdk.yml`, extract the tarball, source
> `environment-setup`, compile with `$CC`.

## 1. Building SDK
```
./kas-container build kas-iot2050-example.yml:kas/opt/sdk.yml
```

Artifacts:
- `sdk-isar-arm64.tar.xz`
- Optional Docker archive

## 2. Installing SDK
```
tar xf sdk-isar-arm64.tar.xz -C /opt
source /opt/sdk/environment-setup
```

## 3. Docker Import
```
docker load -i sdk-iot2050-debian-arm64-docker-archive.tar.xz
```

## 4. Build Test
```
$CC --version
```

## 5. Troubleshooting
| Issue | Fix |
|-------|-----|
| Missing headers | Verify fragment included and SDK build finished OK |
| Wrong compiler picked | Ensure `environment-setup` sourced in current shell |
