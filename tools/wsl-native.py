#!/usr/bin/env python3
"""Add the Linux x64 (glibc) native binaries the lockfile pins to a node_modules tree that npm installed on Windows.

    python3 tools/wsl-native.py            # fetch and unpack what is missing (run inside WSL, in the Windows checkout)
    python3 tools/wsl-native.py --check    # exit 1 naming each missing binary package; writes nothing

The unattended run lives in WSL and works in the Windows checkout (`/mnt/d/Gemail`), where `npm ci` installed only
the win32 builds of the platform packages (lightningcss, @tailwindcss/oxide, the @unrs resolver), so webpack, Tailwind
and ESLint fail under Linux. Each missing package is taken from the lockfile entry npm skipped on Windows (its
`resolved` tarball), checked against the lockfile's `integrity` hash, and unpacked to its own `node_modules/<name>`
folder. Nothing else in the tree is touched, so the Windows install keeps working. A Windows `npm ci` removes these
again; the unattended preflight runs `--check` and names this command.

WORKAROUND: npm installs one platform's optional binaries per tree and has no setting for a second platform (pnpm's
`supportedArchitectures` has no npm equivalent), so the second platform's packages are unpacked here, from the
lockfile's own pins.
Stdlib only.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def wanted(lock: dict) -> list[tuple[str, dict]]:
    """Lockfile entries for Linux x64 glibc binaries whose parent package is installed."""
    out = []
    for key, entry in lock.get("packages", {}).items():
        if not key.startswith("node_modules/") or key.count("node_modules/") != 1:
            continue
        if "linux" not in (entry.get("os") or []) or "x64" not in (entry.get("cpu") or []):
            continue
        if key.endswith("-musl") or "musl" in (entry.get("libc") or []):
            continue
        if not entry.get("resolved") or not entry.get("integrity"):
            continue
        out.append((key, entry))
    return out


def present(key: str) -> bool:
    return (ROOT / key / "package.json").is_file()


def fetch(entry: dict) -> bytes:
    with urllib.request.urlopen(entry["resolved"], timeout=120) as resp:  # the registry URL the lockfile pins
        data = resp.read()
    algo, _, digest = entry["integrity"].partition("-")
    if algo not in ("sha512", "sha384", "sha256") or base64.b64decode(digest) != hashlib.new(algo, data).digest():
        raise SystemExit(f"wsl-native: {entry['resolved']} does not match the lockfile integrity; nothing unpacked")
    return data


def unpack(key: str, data: bytes) -> None:
    target = ROOT / key
    with tempfile.TemporaryDirectory(dir=ROOT / "node_modules") as tmp:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            tar.extractall(tmp, filter="data")  # refuses absolute paths, links out of the folder and devices
        source = Path(tmp) / "package"
        if not (source / "package.json").is_file():
            raise SystemExit(f"wsl-native: {key} tarball has no package/ folder; nothing unpacked")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        os.replace(source, target)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="report missing binaries, write nothing")
    args = parser.parse_args(argv)
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    missing = [(k, e) for k, e in wanted(lock) if not present(k)]
    if args.check:
        for key, entry in missing:
            print(f"wsl-native: missing {key[len('node_modules/'):]}@{entry.get('version')}")
        print(f"wsl-native: {len(missing)} Linux binary package(s) missing"
              + (": run python3 tools/wsl-native.py in WSL" if missing else ""))
        return 1 if missing else 0
    if not (ROOT / "node_modules").is_dir():
        print("wsl-native: node_modules is missing; run npm ci on Windows first", file=sys.stderr)
        return 1
    for key, entry in missing:
        unpack(key, fetch(entry))
        print(f"wsl-native: unpacked {key[len('node_modules/'):]}@{entry.get('version')}")
    print(f"wsl-native: {len(missing)} added, {len(wanted(lock)) - len(missing)} already present")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
