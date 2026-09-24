#!/usr/bin/env python3

"""Hide Cockpit's language selector without deleting translation assets."""

import json
import os
import tempfile


MANIFEST = "/usr/share/cockpit/shell/manifest.json"
# This is the Cockpit manifest API compatibility level, not the Debian
# cockpit package version. The manifest transformation has been verified
# against this API level and must be reviewed when Cockpit changes it.
SUPPORTED_COCKPIT_API = "239"


def main():
    try:
        with open(MANIFEST, encoding="utf-8") as stream:
            manifest = json.load(stream)
    except FileNotFoundError:
        raise SystemExit(f"Cockpit shell manifest not found: {MANIFEST}")
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Cannot read Cockpit shell manifest: {error}")

    if not isinstance(manifest, dict) or not isinstance(manifest.get("requires"), dict):
        raise SystemExit("Unexpected Cockpit shell manifest structure")

    cockpit_api = manifest["requires"].get("cockpit")
    if cockpit_api != SUPPORTED_COCKPIT_API:
        raise SystemExit(
            "Unsupported Cockpit shell manifest API: "
            f"expected {SUPPORTED_COCKPIT_API}, found {cockpit_api!r}"
        )

    locales = manifest.get("locales")
    if locales is None:
        return
    if not isinstance(locales, dict) or "en-us" not in locales:
        raise SystemExit("Unexpected Cockpit shell manifest locales structure")

    del manifest["locales"]
    directory = os.path.dirname(MANIFEST)
    fd, temporary = tempfile.mkstemp(prefix="manifest.json.", dir=directory, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=4)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, os.stat(MANIFEST).st_mode & 0o7777)
        os.replace(temporary, MANIFEST)
    except OSError as error:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise SystemExit(f"Cannot update Cockpit shell manifest: {error}")


if __name__ == "__main__":
    main()