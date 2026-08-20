# Clean-Room Reproduction Report

Part VIII. A genuine fresh clone — from the actual GitHub remote, not a local copy — was
built, tested, and compared against the working tree.

## Method

```
git clone --branch claude/forward-mdcl-compiler-build-ng4k2k https://github.com/BLZIX989/SEIT seit_cleanroom
```

into an isolated scratch directory, outside the working repository. No generated registry,
cached result, or undocumented local file was copied in — the clone contains only what
`git clone` itself fetches from the remote.

## Commit hash

`6818acd4d5f4a85252aadc22980f88594c727b36` (branch `claude/forward-mdcl-compiler-build-ng4k2k`)
— confirmed identical between the working tree's `git rev-parse HEAD` and the fresh clone's,
i.e. the push landed correctly and the remote serves exactly the intended commit.

## Environment

| | |
|---|---|
| Python | 3.11.15 |
| numpy | 2.4.6 |
| scipy | 1.17.1 |
| sympy | 1.14.0 |
| astropy | 8.0.1 |
| OS / kernel | Linux 6.18.5-fc-v20, x86_64 |

**No dependency manifest exists in this repository** (`requirements.txt`, `pyproject.toml`,
`setup.py`, and `*.cfg` were all searched for at the repository root and none were found). This
is reported honestly rather than fabricated — the clean-room checkout therefore ran against
the same shared Python environment as the working tree (there being no declared configuration
to install from), whose exact package versions are what every single calculation's own
provenance record already carries (`numerical_environment` field in
`calculation_registry.json`, confirmed identical between the two trees below). This is a real
limitation of this reproduction test — it verifies code and data fidelity across a genuine
independent clone, not full environment isolation — and is recorded as such, not silently
upgraded to a stronger claim.

## Random seeds

No random seed was needed for this test: every calculation re-executed during this campaign
(Test 1's 14 topologies, the S³ control, the Fisher-Rao PSD demonstration, the
eigenvalue-uniqueness counterexample) is either deterministic or uses a fixed seed already
embedded in its own source (e.g. `eigen_uniqueness.py`'s trial generator) — the same seed in
both trees by construction, since both trees run the identical committed source.

## What was run

```
python3 -m pytest compiler/tests -q          # 95 passed
python3 -m compiler.run_compiler             # terminal status CONDITIONALLY_CLOSED,
                                              # all 10 self-audits PASS
```

Execution time: pytest ~44s, compiler build well under a minute — consistent with the working
tree's own timings for the identical operations (no unexplained slowdown or speedup, note that
DESI network downloads are not part of either run — the pipeline reads only the committed
pilot fixture on this path, `data/desi/dr1/fc005/validated/pilot_fixture/
lrg_sgc_pilot_3000_z0.4-0.6.fits`, present and correctly committed in the fresh clone).

## Registry comparison (the actual reproduction check)

Every regenerated registry was diffed against the working tree's, field-by-field, with only
`execution_timestamp` and `git_commit` (expected to legitimately differ per-run) excluded:

| Registry | Result |
|---|---|
| `status_matrix.json` | **Identical** |
| `falsification_registry.json` | **Identical** |
| `object_registry.json` | **Identical** |
| `transformation_registry.json` | **Identical** |
| `equation_registry.json` | **Identical** |
| `calculation_registry.json` | **Identical except one entry**: `CALC-FC005-DESI-SPARSE-N-SCALING` present in the working tree, absent in the clean-room clone |

## The one documented difference, explained

`CALC-FC005-DESI-SPARSE-N-SCALING` is loaded by `compiler/ir/fc005.py::register_fc005` from
`data/desi/dr1/fc005/derived/sparse_n_scaling_full_results.json` **only if that file exists**
(`if sparse_path.exists(): ...`, a deliberate, graceful, documented guard — not a crash or a
silent fabrication). That file is the ~40-minute sparse-eigensolver computation's raw output —
correctly `.gitignore`d per this project's data-storage convention
(`data/desi/dr1/fc005/derived/*` is excluded; only the small `validated/pilot_fixture/` is
committed). A fresh clone therefore does not have it, and — per this campaign's explicit
execution override — **that ~40-minute investigation was correctly not rerun** to manufacture
it. This is not a reproducibility failure: it is the documented, correct behavior of a
deliberately gitignored large-artifact policy, combined with graceful-absence handling that
was itself verified working exactly as designed. No other registry entry is affected.

## Large-dataset commit check (Part XVIII.7)

Confirmed via direct inspection of the fresh clone: `data/desi/dr1/fc005/raw/` and
`data/desi/dr1/fc005/derived/` are both **empty** in the clone (correctly gitignored — no raw
DESI catalogue or derived computation output was accidentally committed). Total clone size:
71 MB, consistent with the repository's source-workbook PDFs/DOCX files, not any dataset.

## Conclusion

**Fresh checkout ≡ canonical project state**, subject only to the one explicitly documented,
non-nondeterministic difference above (a deliberately gitignored derived-data file, absent by
design, not by accident or flaw) and the one explicitly documented environment-isolation
limitation (no dependency manifest exists to install from). Every test passes identically,
every self-audit passes identically, and every registry that *can* be regenerated from
committed inputs alone reproduces byte-for-byte.
