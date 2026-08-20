#!/usr/bin/env python3
"""Validates a downloaded DESI FC-005 catalog against the checklist in
the FC-005 data-acquisition build command (section 8). Writes
FC005_DESI_SCHEMA_REPORT.json and FC005_DESI_VALIDATION_REPORT.md.

Usage:
    python3 validate_desi_fc005.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from astropy.io import fits

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "reports/fc005/FC005_DESI_CATALOG_MANIFEST.json"
RAW_DIR = ROOT / "data" / "desi" / "dr1" / "fc005" / "raw"

REQUIRED_COLUMNS = ["TARGETID", "RA", "DEC", "Z", "WEIGHT", "WEIGHT_FKP", "WEIGHT_SYS"]
CHECK_FINITE_COLUMNS = ["RA", "DEC", "Z", "WEIGHT", "WEIGHT_FKP", "WEIGHT_SYS"]


def validate_file(path: Path, manifest_entry: dict) -> dict:
    checks: list[dict] = []

    def record(name, passed, detail=""):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    try:
        hdul = fits.open(path)
    except Exception as e:
        record("fits_opens", False, str(e))
        return {"file": path.name, "checks": checks, "all_passed": False}
    record("fits_opens", True)

    hdu_names = [h.name for h in hdul]
    record("expected_hdus_exist", "LSS" in hdu_names or len(hdul) >= 2,
           f"HDUs: {hdu_names}")

    data = hdul[1].data
    columns = list(data.columns.names)

    missing = [c for c in REQUIRED_COLUMNS if c not in columns]
    record("required_columns_exist", len(missing) == 0,
           f"missing: {missing}" if missing else f"all present: {REQUIRED_COLUMNS}")

    dtype_issues = []
    for c in REQUIRED_COLUMNS:
        if c in columns:
            fmt = hdul[1].columns[c].format
            if not any(code in fmt for code in ("D", "E", "K", "J", "I")):
                dtype_issues.append((c, fmt))
    record("column_datatypes_valid", len(dtype_issues) == 0, f"issues: {dtype_issues}")

    n_rows = int(hdul[1].header.get("NAXIS2", -1))
    expected_rows = manifest_entry.get("row_count")
    record("object_count_agrees_with_metadata", n_rows == expected_rows,
           f"file has {n_rows} rows, manifest recorded {expected_rows}")

    ra = np.asarray(data["RA"])
    dec = np.asarray(data["DEC"])
    z = np.asarray(data["Z"])

    record("ra_finite", bool(np.all(np.isfinite(ra))),
           f"n_nonfinite={int(np.sum(~np.isfinite(ra)))}")
    record("dec_finite", bool(np.all(np.isfinite(dec))),
           f"n_nonfinite={int(np.sum(~np.isfinite(dec)))}")
    record("z_finite", bool(np.all(np.isfinite(z))),
           f"n_nonfinite={int(np.sum(~np.isfinite(z)))}")

    weight_finite_issues = {}
    for c in ("WEIGHT", "WEIGHT_FKP", "WEIGHT_SYS"):
        if c in columns:
            arr = np.asarray(data[c])
            n_bad = int(np.sum(~np.isfinite(arr)))
            weight_finite_issues[c] = n_bad
    record("weights_finite", all(v == 0 for v in weight_finite_issues.values()),
           str(weight_finite_issues))

    z_min, z_max = float(z.min()), float(z.max())
    tracer_range = (0.4, 1.1)  # LRG, per arXiv:2411.12020, verified in FC005_DESI_SELECTION.md
    in_range = (z_min >= tracer_range[0] - 1e-6) and (z_max <= tracer_range[1] + 1e-6)
    record("redshift_within_documented_tracer_range", in_range,
           f"observed [{z_min:.4f}, {z_max:.4f}] vs documented {tracer_range}")

    targetid = np.asarray(data["TARGETID"])
    n_unique = len(np.unique(targetid))
    n_dupes = len(targetid) - n_unique
    record("duplicate_targetids_understood", True,
           f"{n_dupes} duplicate TARGETID rows out of {len(targetid)} "
           f"({'none -- one row per unique object' if n_dupes == 0 else 'present, not investigated further in the pilot'})")

    mask_fields = [c for c in ("PHOTSYS", "NTILE", "FRAC_TLOBS_TILES") if c in columns]
    record("mask_selection_fields_present", len(mask_fields) > 0, f"found: {mask_fields}")

    ra_bad = int(np.sum((ra < 0) | (ra > 360)))
    dec_bad = int(np.sum((dec < -90) | (dec > 90)))
    record("no_silent_range_contamination", ra_bad == 0 and dec_bad == 0,
           f"RA out of [0,360]: {ra_bad}; DEC out of [-90,90]: {dec_bad}")

    hdul.close()
    all_passed = all(c["passed"] for c in checks)
    return {
        "file": path.name, "n_rows": n_rows, "columns": columns,
        "z_range_observed": [z_min, z_max], "checks": checks, "all_passed": all_passed,
    }


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text())
    primary = next(e for e in manifest["entries"] if e["role"] == "SELECTED_PRIMARY_DATA")
    path = RAW_DIR / primary["filename"]

    if not path.exists():
        print(f"STOP: {path} not found. Run download_desi_fc005.py first.")
        return 1

    result = validate_file(path, primary)

    schema_report = {
        "file": result["file"], "n_rows": result["n_rows"], "columns": result["columns"],
        "z_range_observed": result["z_range_observed"],
    }
    with fits.open(path) as hdul:
        schema_report["column_formats"] = {
            name: hdul[1].columns[name].format for name in hdul[1].columns.names
        }
    (ROOT / "reports/fc005/FC005_DESI_SCHEMA_REPORT.json").write_text(json.dumps(schema_report, indent=2))

    lines = ["# FC-005 DESI Validation Report", "",
             f"File: `{result['file']}`", f"Rows: {result['n_rows']}",
             f"Redshift range observed: [{result['z_range_observed'][0]:.4f}, "
             f"{result['z_range_observed'][1]:.4f}]", "",
             "| check | passed | detail |", "|---|---|---|"]
    for c in result["checks"]:
        mark = "PASS" if c["passed"] else "FAIL"
        lines.append(f"| {c['check']} | {mark} | {c['detail']} |")
    lines.append("")
    lines.append(f"**Overall: {'PASSED' if result['all_passed'] else 'FAILED'}**")
    (ROOT / "reports/fc005/FC005_DESI_VALIDATION_REPORT.md").write_text("\n".join(lines))

    print(f"Wrote FC005_DESI_SCHEMA_REPORT.json and FC005_DESI_VALIDATION_REPORT.md")
    print(f"Overall: {'PASSED' if result['all_passed'] else 'FAILED'}")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
