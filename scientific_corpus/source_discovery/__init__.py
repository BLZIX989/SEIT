"""Phase 13, Phases C+D (master brief): scientific source discovery and
legitimate acquisition.

Scope discipline, per the governing rule at the top of the brief: this
package produces SOURCE evidence (bibliographic metadata + acquired
files with real byte hashes), never EQUATION evidence. No equation is
extracted from anything in this package -- search-result metadata and
abstracts are discovery evidence only, never mathematical content.
Equation/variable/operator extraction is a separate, later pipeline
that has not been built (see PHASE13_PHASE_A_B_STATUS_REPORT.md and
PHASE13_SOURCE_DISCOVERY_REPORT.md for exactly what has and hasn't been
attempted).

Channel used this slice: the arXiv API (export.arxiv.org/api/query),
the only Level 2 authoritative database this slice actually queries.
Other Level 2 sources named in the brief (INSPIRE-HEP, NASA ADS, NIST/
DLMF, HEPData, Crossref, OpenAlex) have NOT been implemented -- see the
report's explicit scope statement rather than assuming silent coverage.

Legal/access discipline actually enforced:
  - export.arxiv.org/robots.txt disallows "/" for general crawlers, but
    arXiv's own official API documentation (info.arxiv.org/help/api/
    user-manual.html) describes and invites exactly this
    export.arxiv.org/api/query usage pattern as the documented API
    surface, with a requested 3-second delay between calls -- this
    client enforces a minimum 3.0s gap, enforced in code
    (arxiv_client.py::_RateLimiter), not just documented as a promise.
  - arxiv.org/robots.txt (the abstract/PDF host, a different service
    from the API host) explicitly Disallows "/e-print" and "/src" for
    automated agents -- this package therefore does NOT acquire LaTeX
    source packages via those endpoints. Only "/pdf" and "/abs" (both
    explicitly Allowed) are ever fetched, with the site's own declared
    Crawl-delay: 15 honored between PDF fetches.
"""
