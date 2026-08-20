"""Cross-reference newly discovered sources against the existing project
corpus (brief section XX). If a discovered arXiv id matches a source
already ingested in Phase A/B (scientific_corpus.schema.Source records,
e.g. LIT-TONG-ST), link rather than duplicate -- the existing source's
own id and provenance are preserved untouched.
"""
from __future__ import annotations

from scientific_corpus.schema import Source
from scientific_corpus.source_discovery.schema import DiscoveredSource


def _bare_arxiv_id(arxiv_id: str | None) -> str | None:
    if not arxiv_id:
        return None
    # strip a trailing "vN" version suffix if present
    if "v" in arxiv_id and arxiv_id.rsplit("v", 1)[-1].isdigit():
        return arxiv_id.rsplit("v", 1)[0]
    return arxiv_id


def link_existing_sources(
    discovered: list[DiscoveredSource], existing_sources: list[Source],
) -> tuple[list[DiscoveredSource], list[dict]]:
    """Marks any DiscoveredSource whose bare arXiv id matches an existing
    Phase A/B Source's arxiv_id as LINK_EXISTING_SOURCE (duplicate_group
    set, acquisition_status left DISCOVERED_ONLY so it is never
    re-acquired as if new). Returns (all discovered sources, link records)."""
    existing_by_arxiv: dict[str, str] = {}
    for s in existing_sources:
        bare = _bare_arxiv_id(s.arxiv_id)
        if bare:
            existing_by_arxiv[bare] = s.source_id

    links = []
    for d in discovered:
        bare = _bare_arxiv_id(d.arxiv_id)
        existing_id = existing_by_arxiv.get(bare) if bare else None
        if existing_id:
            d.duplicate_group = f"LINK_EXISTING_SOURCE:{existing_id}"
            d.parent_source_id = existing_id
            d.acquisition_status = "DISCOVERED_ONLY"
            links.append({
                "discovered_source_id": d.source_id, "arxiv_id": d.arxiv_id,
                "linked_existing_source_id": existing_id, "relation": "LINK_EXISTING_SOURCE",
            })
    return discovered, links
