#!/usr/bin/env python3
"""Downloads the FC-005 DESI DR1 catalog entries marked "REQUIRED" in
FC005_DESI_CATALOG_MANIFEST.json, verifies each against its recorded
sha256 checksum, and refuses to accept a partial/corrupt file.

Usage:
    python3 download_desi_fc005.py            # required entries only
    python3 download_desi_fc005.py --include-optional
    python3 download_desi_fc005.py --dest data/desi/dr1/fc005/raw
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "FC005_DESI_CATALOG_MANIFEST.json"
DEFAULT_DEST = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw"


def sha256_of(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def download_one(entry: dict, dest_dir: Path) -> dict:
    url = entry["url"]
    filename = entry.get("filename") or url.rsplit("/", 1)[-1]
    out_path = dest_dir / filename
    expected_size = entry.get("file_size_bytes")
    expected_sha256 = entry.get("checksum_sha256")

    result = {"filename": filename, "url": url, "status": "PENDING"}

    tmp_path = out_path.with_suffix(out_path.suffix + ".part")
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            content_length = int(r.headers.get("content-length", 0)) or None
            if expected_size and content_length and content_length != expected_size:
                result["status"] = "FAILED"
                result["reason"] = (
                    f"server content-length {content_length} != manifest "
                    f"file_size_bytes {expected_size} -- refusing to download, "
                    f"manifest may be stale"
                )
                return result
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
    except requests.RequestException as e:
        result["status"] = "FAILED"
        result["reason"] = f"HTTP request failed: {e}"
        if tmp_path.exists():
            tmp_path.unlink()
        return result

    actual_size = tmp_path.stat().st_size
    if expected_size and actual_size != expected_size:
        result["status"] = "FAILED"
        result["reason"] = f"downloaded size {actual_size} != expected {expected_size}"
        tmp_path.unlink()
        return result

    if expected_sha256:
        actual_sha256 = sha256_of(tmp_path)
        if actual_sha256 != expected_sha256:
            result["status"] = "FAILED"
            result["reason"] = f"sha256 mismatch: got {actual_sha256}, expected {expected_sha256}"
            tmp_path.unlink()
            return result
        result["checksum_verified"] = True

    tmp_path.rename(out_path)
    result["status"] = "OK"
    result["path"] = str(out_path)
    result["size_bytes"] = actual_size
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    ap.add_argument("--include-optional", action="store_true",
                     help="also download entries marked OPTIONAL (e.g. the random catalog)")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text())
    args.dest.mkdir(parents=True, exist_ok=True)

    wanted_roles = {"SELECTED_PRIMARY_DATA"}
    if args.include_optional:
        wanted_roles.add("RANDOM_CATALOG_DEFERRED")

    results = []
    for entry in manifest["entries"]:
        if entry["role"] not in wanted_roles:
            continue
        print(f"Downloading {entry['filename']} ({entry.get('file_size_human', '?')}) ...")
        r = download_one(entry, args.dest)
        print(f"  -> {r['status']}" + (f" ({r.get('reason')})" if r.get("reason") else ""))
        results.append(r)

    failed = [r for r in results if r["status"] != "OK"]
    log_path = args.dest.parent / "metadata" / "download_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {log_path}")

    if failed:
        print(f"\n{len(failed)} download(s) FAILED. See {log_path}.", file=sys.stderr)
        return 1
    print(f"\nAll {len(results)} requested download(s) OK and checksum-verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
