#!/usr/bin/env bash
# Validate patches used by the U-Boot and Linux recipes.

set -euo pipefail

patch_dirs=(
    meta/recipes-bsp/u-boot/files
    meta/recipes-kernel/linux/files/patches
)

uboot_checkpatch=${1:?path to U-Boot checkpatch.pl is required}
linux_checkpatch=${2:?path to Linux checkpatch.pl is required}

check_patch_metadata() {
    local patch=$1
    local diffstat
    local actual_stats

    diffstat=$(awk '/^[[:space:]]*[0-9]+ files? changed, / { line = $0 } END { print line }' "$patch")
    if [[ -z $diffstat ]]; then
        printf '%s: missing diffstat summary\n' "$patch" >&2
        return 1
    fi

    actual_stats=$(git apply --numstat "$patch" | awk '
        $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ {
            files++
            additions += $1
            deletions += $2
        }
        $1 == "-" && $2 == "-" {
            files++
        }
        END {
            printf "%d %d %d\n", files, additions, deletions
        }
    ')
    if ! grep -Eq '^[[:space:]]*[0-9]+ files? changed(, [0-9]+ insertions?\(\+\))?(, [0-9]+ deletions?\(-\))?[[:space:]]*$' <<< "$diffstat" &&
        ! grep -Eq '^[[:space:]]*[0-9]+ files? changed, [0-9]+ deletions?\(-\)[[:space:]]*$' <<< "$diffstat"; then
        printf '%s: invalid diffstat summary: %s\n' "$patch" "$diffstat" >&2
        return 1
    fi
    expected_stats="$(sed -E 's/^[[:space:]]*([0-9]+) files? changed.*/\1/' <<< "$diffstat")"
    additions=$(sed -nE 's/.*,[[:space:]]*([0-9]+) insertions?\(\+\).*/\1/p' <<< "$diffstat")
    deletions=$(sed -nE 's/.*,[[:space:]]*([0-9]+) deletions?\(-\).*/\1/p' <<< "$diffstat")
    expected_stats+=" ${additions:-0} ${deletions:-0}"
    if [[ $actual_stats != "$expected_stats" ]]; then
        printf '%s: diffstat does not match the actual diff (header: %s; actual: %s)\n' \
            "$patch" "$expected_stats" "$actual_stats" >&2
        return 1
    fi

    awk '
        NR == 1 && $0 != "From " "0000000000000000000000000000000000000000" " Mon Sep 17 00:00:00 2001" {
            print FILENAME ":1: patch is not generated with --zero-commit" > "/dev/stderr"
            invalid = 1
        }
        /^Subject: \[PATCH [0-9]+\// {
            print FILENAME ":" NR ": numbered patch series is not allowed; use --no-numbered" > "/dev/stderr"
            invalid = 1
        }
        /^index / {
            split($2, hashes, "\\.\\.")
            if (length(hashes[1]) > 12 || length(hashes[2]) > 12) {
                print FILENAME ":" NR ": index hash is longer than 12 characters; use --abbrev=12" > "/dev/stderr"
                invalid = 1
            }
        }
        /^-- $/ {
            signature = 1
        }
        END {
            if (signature) {
                print FILENAME ": patch contains a git-format-patch signature; use --no-signature" > "/dev/stderr"
                invalid = 1
            }
            if (!separator) {
                print FILENAME ": missing format-patch separator" > "/dev/stderr"
                invalid = 1
            }
            if (invalid)
                exit 1
        }
        /^---$/ {
            if (previous ~ /^[[:space:]]*$/) {
                print FILENAME ":" NR ": blank line before the diffstat separator; use the format-patch output without an extra blank line" > "/dev/stderr"
                invalid = 1
            }
            separator = 1
            next
        }
        !separator && /^[[:space:]]+$/ {
            print FILENAME ":" NR ": whitespace-only line in patch metadata" > "/dev/stderr"
            invalid = 1
        }
        { previous = $0 }
    ' "$patch"
}

mapfile -d '' patches < <(find "${patch_dirs[@]}" -type f -name '*.patch' -print0 | sort -z)
if ((${#patches[@]} == 0)); then
    echo 'No recipe patches found.' >&2
    exit 1
fi

for patch in "${patches[@]}"; do
    echo "Checking ${patch}"

    # git mailinfo is the parser used by git-am.  This catches malformed
    # format-patch mail without requiring the source tree the patch targets.
    tmpdir=$(mktemp -d)
    trap 'rm -rf "$tmpdir"' EXIT
    git mailinfo "$tmpdir/message" "$tmpdir/content" < "$patch" >/dev/null

    # Check the format-patch options required by CONTRIBUTING.md.  In
    # particular, whitespace-only metadata lines were the defect fixed by
    # PR #687.
    check_patch_metadata "$patch"

    # Use the component-maintainer checkpatch implementation.  Blank lines in
    # unified diffs necessarily carry a trailing space, so that diagnostic is
    # intentionally excluded; metadata whitespace is checked above.  Existing
    # upstream patches may contain intentional long lines, so do not reject
    # those style warnings in this format check.
    if [[ $patch == meta/recipes-bsp/u-boot/* ]]; then
        checkpatch=$uboot_checkpatch
    else
        checkpatch=$linux_checkpatch
    fi
    perl "$checkpatch" --no-tree --ignore TRAILING_WHITESPACE,LONG_LINE "$patch" >/dev/null

    rm -rf "$tmpdir"
    trap - EXIT
done
