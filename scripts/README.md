# scripts/

One-off campaign scripts (DESI acquisition/validation/diagnostics
runners, report/matrix generators). None of these are part of the
compiler's own execution path — `compiler/run_compiler.py` never
imports anything from this directory. They are kept for
reproducibility and provenance of the campaign reports under
`reports/`.

Each script computes its own repo root as
`Path(__file__).resolve().parent.parent` and writes/reads files by
path relative to that root, so they must be run from anywhere with the
repo checked out (no dependency on the current working directory) —
e.g. `python3 scripts/generate_dependency_closure_audit.py`.

The DESI download/pilot/gate scripts (`download_desi_fc005.py`,
`run_desi_*.py`) require network access to the public DESI DR1 release
and are not expected to succeed in a sandboxed environment without
that access.
