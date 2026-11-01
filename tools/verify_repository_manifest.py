#!/usr/bin/env python3
"""Read-only SHA-256 inventory check for an exact Git checkout.

A passing result shows only that tracked bytes match the untrusted manifest.
It does NOT authenticate author, keys, source, human decisions, field data or ISO.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

HEX = re.compile(r"[0-9a-f]{64}\Z")


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _tracked(root: Path):
    run = subprocess.run(["git", "-C", str(root), "ls-files", "--stage", "-z"],
                         check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=15)
    files = {}
    for item in run.stdout.split(b"\0"):
        if not item:
            continue
        header, raw_path = item.split(b"\t", 1)
        mode, _blob, stage = header.decode("ascii").split(" ")
        path = raw_path.decode("utf-8", errors="strict")
        if path in files or stage != "0":
            raise ValueError("unmerged or duplicate Git index entry")
        if mode not in {"100644", "100755"}:
            raise ValueError("gitlink, symlink or unsupported Git mode")
        files[path] = mode
    return files


def _path_safe(path: object) -> bool:
    if not isinstance(path, str) or not path or path.startswith("/"):
        return False
    if "\\" in path or "\x00" in path or any(ord(c) < 32 for c in path):
        return False
    pure = PurePosixPath(path)
    return not any(part in {"", ".", ".."} for part in path.split("/")) and pure.as_posix() == path


def verify(root: Path, manifest_name: str = "SHA256SUMS.json") -> dict:
    problems = []
    try:
        root = root.resolve(strict=True)
        if not _path_safe(manifest_name):
            raise ValueError("unsafe manifest name")
        tracked = _tracked(root)
        manifest = json.loads((root / manifest_name).read_text(encoding="utf-8"),
                              object_pairs_hook=_no_duplicate_keys)
        if not isinstance(manifest, dict) or manifest.get("self_excluded") is not True:
            raise ValueError("self-exclusion absent")
        if manifest.get("algorithm") != "SHA-256":
            raise ValueError("unexpected digest algorithm")
        records = manifest.get("files")
        if not isinstance(records, list) or not records:
            raise ValueError("empty or invalid manifest entries")
        paths, entries = set(), []
        for entry in records:
            if not isinstance(entry, dict):
                raise ValueError("non-object file entry")
            path, expected = entry.get("path"), entry.get("sha256")
            if not _path_safe(path) or path == manifest_name:
                raise ValueError("unsafe path or manifest self-hash")
            if path in paths:
                raise ValueError("duplicate path")
            if not isinstance(expected, str) or HEX.fullmatch(expected) is None:
                raise ValueError("noncanonical SHA-256")
            paths.add(path)
            entries.append((path, expected))
        if manifest.get("file_count") != len(entries):
            raise ValueError("file count mismatch")
        if set(tracked) != paths | {manifest_name}:
            raise ValueError("Git tracked tree differs from inventory")
        aggregate = hashlib.sha256()
        for path, expected in sorted(entries):
            target = root / path
            if not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to(root):
                raise ValueError("missing file or unsafe filesystem entry")
            digest = hashlib.sha256()
            with target.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != expected:
                raise ValueError("file hash mismatch: " + path)
            aggregate.update(f"{path}\0{expected}\n".encode("utf-8"))
        if manifest.get("global_sha256") != aggregate.hexdigest():
            raise ValueError("global aggregate hash mismatch")
        return {"status": "LOCAL_INTEGRITY_ONLY", "files_checked": len(entries),
                "global_sha256": aggregate.hexdigest(), "promotion": "BLOCKED",
                "limitations": ["manifest_is_not_signed", "not_external_validation",
                                "not_field_truth", "not_human_approval"], "findings": []}
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        problems.append(str(exc))
        return {"status": "BLOCKED", "files_checked": 0, "promotion": "BLOCKED",
                "findings": problems}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--manifest", default="SHA256SUMS.json")
    args = parser.parse_args()
    report = verify(args.root, args.manifest)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "LOCAL_INTEGRITY_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
