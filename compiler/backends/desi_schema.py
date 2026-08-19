"""DESI column -> FC-005 canonical field schema map (spec section 9 of
the FC-005 data-acquisition build command). Every canonical field must
be traceable back to its original DESI column and source file -- no
physical column is renamed without this explicit map, and
`load_d_desi` attaches file-level provenance to the loaded table.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from astropy.io import fits

# DESI column name -> FC-005 canonical field name. Identity here (DESI's
# own naming already matches the canonical names used throughout
# compiler/backends/desi_graph.py and desi_fc005_pipeline.py) -- recorded
# explicitly per spec section 9, not assumed.
SCHEMA_MAP: dict[str, str] = {
    "TARGETID": "TARGETID",
    "RA": "RA",
    "DEC": "DEC",
    "Z": "Z",
    "WEIGHT": "WEIGHT",
    "WEIGHT_FKP": "WEIGHT_FKP",
    "WEIGHT_SYS": "WEIGHT_SYS",
    "WEIGHT_ZFAIL": "WEIGHT_ZFAIL",
    "WEIGHT_COMP": "WEIGHT_COMP",
    "NTILE": "NTILE",              # mask/coverage: number of overlapping tiles
    "PHOTSYS": "PHOTSYS",          # mask/region: photometric system (N/S)
    "FRAC_TLOBS_TILES": "FRAC_TLOBS_TILES",  # completeness fraction
    "NX": "NX",                    # selection function n(z) at each object's redshift
}

REQUIRED_CANONICAL_FIELDS = ["TARGETID", "RA", "DEC", "Z", "WEIGHT", "WEIGHT_FKP", "WEIGHT_SYS"]


@dataclass
class DDesiTable:
    canonical: dict[str, np.ndarray]
    source_file: str
    source_url: str
    checksum_sha256: str
    n_rows: int
    schema_map: dict[str, str] = field(default_factory=lambda: dict(SCHEMA_MAP))


def load_d_desi(fits_path: Path, *, source_url: str, checksum_sha256: str) -> DDesiTable:
    """Loads a DESI clustering .dat.fits file into the canonical D_DESI
    table, applying SCHEMA_MAP and recording provenance back to the exact
    file/URL/checksum this data came from."""
    with fits.open(fits_path) as hdul:
        data = hdul[1].data
        available = set(data.columns.names)
        canonical = {}
        for desi_col, canonical_field in SCHEMA_MAP.items():
            if desi_col in available:
                canonical[canonical_field] = np.asarray(data[desi_col])
        missing_required = [f for f in REQUIRED_CANONICAL_FIELDS if f not in canonical]
        if missing_required:
            raise ValueError(f"D_DESI missing required canonical fields: {missing_required}")
        n_rows = int(hdul[1].header.get("NAXIS2", len(canonical["RA"])))

    return DDesiTable(
        canonical=canonical, source_file=str(fits_path), source_url=source_url,
        checksum_sha256=checksum_sha256, n_rows=n_rows,
    )


def apply_redshift_cut(table: DDesiTable, z_min: float, z_max: float) -> DDesiTable:
    z = table.canonical["Z"]
    mask = (z >= z_min) & (z < z_max)
    cut = {k: v[mask] for k, v in table.canonical.items()}
    return DDesiTable(
        canonical=cut, source_file=table.source_file, source_url=table.source_url,
        checksum_sha256=table.checksum_sha256, n_rows=int(mask.sum()), schema_map=table.schema_map,
    )
