"""arXiv API client (brief section IV Level 2, section XII network
engineering). Two layers, deliberately separated so the parser is
testable offline (brief section XXIII):

  - `fetch_raw(query_text, ...)` performs the actual HTTP GET against
    export.arxiv.org/api/query. Real network I/O; not used by ordinary
    (offline) tests.
  - `parse_atom_feed(xml_bytes)` is a pure function over Atom XML bytes
    -- fully testable against fixture strings, no network required.

Rate limiting: arXiv's own API documentation (info.arxiv.org/help/api/
user-manual.html) asks for "a 3 second delay" between calls; `_RateLimiter`
enforces a minimum 3.0s gap between real HTTP requests in code, not just
as a documented intention. Retries use exponential backoff (2s, 4s, 8s)
on transient (5xx/timeout) failures, capped at 3 attempts, and never
retry on a 4xx (that is a real access/not-found outcome, not a transient
fault -- retrying it would misrepresent the source's actual status).
"""
from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

ARXIV_API_BASE = "https://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
OPENSEARCH_NS = "{http://a9.com/-/spec/opensearch/1.1/}"


class RateLimiter:
    def __init__(self, min_interval_seconds: float = 3.0):
        self.min_interval = min_interval_seconds
        self._last_call: float | None = None

    def wait(self) -> None:
        if self._last_call is not None:
            elapsed = time.monotonic() - self._last_call
            remaining = self.min_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_call = time.monotonic()


_RATE_LIMITER = RateLimiter(min_interval_seconds=3.0)


@dataclass
class ArxivEntry:
    arxiv_id: str          # bare id, e.g. "1301.6896", version stripped
    version: str | None    # e.g. "v1"
    title: str
    authors: list[str]
    summary: str
    published: str | None
    updated: str | None
    categories: list[str]
    abs_url: str | None
    pdf_url: str | None
    doi: str | None


def fetch_raw(query_text: str, *, max_results: int = 10, start: int = 0,
               timeout: float = 20.0, max_retries: int = 3) -> bytes:
    """Real network call. Rate-limited (>=3s between calls, enforced
    globally across the process) and retried with exponential backoff
    only on transient failures."""
    params = {
        "search_query": f"all:{query_text}",
        "start": str(start), "max_results": str(max_results),
    }
    url = f"{ARXIV_API_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "UOC-SEIT-research-corpus/0.1 (Phase 13 Phase C/D; "
                      "non-commercial academic research corpus construction)"
    })
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        _RATE_LIMITER.wait()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                raise  # real access outcome, not transient -- do not retry
            last_exc = e
        except (urllib.error.URLError, TimeoutError) as e:
            last_exc = e
        if attempt < max_retries - 1:
            time.sleep(2 ** (attempt + 1))
    assert last_exc is not None
    raise last_exc


def parse_atom_feed(xml_bytes: bytes) -> list[ArxivEntry]:
    """Pure function -- no network. Parses the arXiv Atom feed format."""
    root = ET.fromstring(xml_bytes)
    entries = []
    for entry_el in root.findall(f"{ATOM_NS}entry"):
        raw_id = (entry_el.findtext(f"{ATOM_NS}id") or "").strip()
        # e.g. "http://arxiv.org/abs/1301.6896v1" -> id "1301.6896", version "v1".
        # Old-style ids carry an archive prefix that must be preserved --
        # "http://arxiv.org/abs/math/0002194v2" -> "math/0002194", "v2"
        # (splitting on the LAST "/" only, as a naive tail split would,
        # silently drops the "math/" prefix and corrupts the identifier).
        tail = raw_id.split("/abs/", 1)[-1] if "/abs/" in raw_id else raw_id.rsplit("/", 1)[-1]
        if "v" in tail and tail.rsplit("v", 1)[-1].isdigit():
            bare_id, version = tail.rsplit("v", 1)
            version = f"v{version}"
        else:
            bare_id, version = tail, None

        title = " ".join((entry_el.findtext(f"{ATOM_NS}title") or "").split())
        summary = " ".join((entry_el.findtext(f"{ATOM_NS}summary") or "").split())
        authors = [
            (a.findtext(f"{ATOM_NS}name") or "").strip()
            for a in entry_el.findall(f"{ATOM_NS}author")
        ]
        categories = [
            c.get("term", "") for c in entry_el.findall(f"{ATOM_NS}category") if c.get("term")
        ]
        published = entry_el.findtext(f"{ATOM_NS}published")
        updated = entry_el.findtext(f"{ATOM_NS}updated")
        doi = entry_el.findtext(f"{ARXIV_NS}doi")

        abs_url, pdf_url = None, None
        for link_el in entry_el.findall(f"{ATOM_NS}link"):
            href = link_el.get("href")
            if link_el.get("title") == "pdf":
                pdf_url = href
            elif link_el.get("rel") == "alternate":
                abs_url = href

        entries.append(ArxivEntry(
            arxiv_id=bare_id, version=version, title=title, authors=authors,
            summary=summary, published=published, updated=updated,
            categories=categories, abs_url=abs_url, pdf_url=pdf_url, doi=doi,
        ))
    return entries


def parse_total_results(xml_bytes: bytes) -> int:
    root = ET.fromstring(xml_bytes)
    text = root.findtext(f"{OPENSEARCH_NS}totalResults")
    return int(text) if text else 0
