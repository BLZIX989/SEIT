# Literature Download Manifest — Human-Readable

Companion to `LITERATURE_DOWNLOAD_MANIFEST.json`. Phase L0-A, external physics literature
acquisition, run 2026-08-19.

## Acquired (2 of 4 requested primary sources)

| Source ID | Title | Author | Route used | Pages | SHA256 (first 16 hex) |
|---|---|---|---|---|---|
| `LIT-TONG-ST` | String Theory | David Tong | archival mirror (arXiv:0908.0333v3) | 218 | `b267b9d7bb717e8e` |
| `LIT-KIRITSIS-SST` | Introduction to Superstring Theory | Elias Kiritsis | primary (arXiv:hep-th/9709062v2) | 249 | `7f7c2e4665c5b614` |

## Failed (2 of 4 requested primary sources — both Cambridge/damtp.cam.ac.uk)

| Source ID | Title | Attempted URL | Failure |
|---|---|---|---|
| `LIT-TONG-SM-CAMBRIDGE` | The Standard Model | `damtp.cam.ac.uk/user/tong/sm/standardmodel.pdf` | TLS chain failure (missing intermediate cert on the origin server), confirmed 2 independent ways; no archival URL was supplied |
| `LIT-TONG-GAUGE-CAMBRIDGE` | Lectures on Gauge Theory (course index page) | `damtp.cam.ac.uk/user/tong/gaugetheory.html` | Same failure class; page itself unreachable, so its 5 named sub-PDFs (Yang-Mills, Anomalies, Lattice Gauge Theory, Chiral Symmetry Breaking, Large N) could not even be enumerated, let alone downloaded |

**The Tong String Theory Cambridge URL also failed identically** — it is not in the "failed" table
above only because an archival mirror (arXiv:0908.0333) was explicitly pre-authorized in the
instructing message and used successfully as the fallback. See `acquisition_failures` in the JSON
manifest for the full diagnostic detail (all three `damtp.cam.ac.uk` requests fail with the same
root cause: the server's TLS certificate chain is missing its intermediate, verified with
`openssl s_client -proxy`, distinct from a proxy policy block).

## What this means for corpus coverage

The Gauge/Standard-Model branch's *string-theory-specific* literature support in this phase comes
only from what Tong's String Theory notes and Kiritsis's Introduction to Superstring Theory
themselves say about gauge symmetry emergence, D-branes, and compactification-generated gauge
groups (§VI/§XI of the specification) — **not** from Tong's dedicated Standard Model or Gauge
Theory lecture notes, which could not be acquired this phase. This repository's *prior* L0
phase already holds a separate, partial (Chapter-1-only) extraction of Tong's Standard Model
notes acquired via a chat upload; that material is not merged into the string-theory-specific
deliverables produced here, to keep provenance chains distinct and honest.

## No fabrication

No URL, checksum, page count, or bibliographic detail in this manifest was invented. Every
`SHA256` and `PAGE_COUNT` value was computed directly from the downloaded file
(`hashlib.sha256`, `pypdf.PdfReader`). Every failure was reproduced and diagnosed before being
recorded, not assumed.
