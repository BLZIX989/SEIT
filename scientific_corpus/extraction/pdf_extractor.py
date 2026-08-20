"""PDF text extraction (brief section VII). Uses pypdf -- the only PDF
library available in this environment (no pdfplumber/PyMuPDF) -- to pull
real text from the PDFs Phase 13 actually acquired.

Deliberate, disclosed limitation: pypdf's text extraction from a
rendered PDF does NOT recover LaTeX source or any math-markup structure
-- it returns the linear sequence of glyphs the PDF renderer laid out,
with no reliable way to distinguish "this glyph sequence is an equation"
from "this glyph sequence is a sentence that happens to contain a Greek
letter or an equals sign." Given that, this module does NOT attempt to
produce structured EquationRecord entries from PDF text -- doing so
would mean silently promoting unreliable guesses to equation-registry
entries, which brief section VII explicitly forbids ("mark the equation
EXTRACTION_UNCERTAIN... do not silently repair mathematical notation").
Instead, every candidate equation-bearing line found by a conservative
heuristic is routed to the review queue only (brief section XXV: "the
system must prefer UNRESOLVED over an incorrect automatic
interpretation").
"""
from __future__ import annotations

import re
from pathlib import Path

from scientific_corpus.extraction.schema import ReviewItem, stable_id

_MATH_CHARS = re.compile(
    r"[=+×÷∂∇∫∑√≈≤≥∞∮⊗⊕±∧∨¬∀∃∈∉⊂⊆∼≃≅ΓΔΘΛΞΠΣΦΨΩαβγδεζηθικλμνξπρστυφχψω"
    r"₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹]"
)
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "to", "for", "is", "are",
    "was", "were", "this", "that", "with", "as", "by", "we", "it", "be",
    "on", "at", "from", "which", "can", "has", "have",
}


def _line_is_candidate_equation(line: str) -> bool:
    stripped = line.strip()
    if not (3 <= len(stripped) <= 200):
        return False
    math_hits = len(_MATH_CHARS.findall(stripped))
    if math_hits == 0:
        return False
    words = re.findall(r"[A-Za-z]+", stripped)
    stopword_hits = sum(1 for w in words if w.lower() in _STOPWORDS)
    # a real sentence has many stopwords relative to its length; a
    # rendered equation line almost never does
    if len(words) > 0 and stopword_hits / len(words) > 0.15:
        return False
    return True


def extract_pdf_review_candidates(pdf_path: Path, source_id: str,
                                   max_pages: int | None = None) -> tuple[list[ReviewItem], dict]:
    """Real pypdf text extraction, page by page. Returns (review_items,
    stats). Never raises past this function -- a page or file that fails
    to parse is recorded in stats, not silently skipped without a trace."""
    import pypdf

    stats = {"pages_processed": 0, "pages_failed": 0, "candidate_lines": 0, "total_lines": 0}
    items: list[ReviewItem] = []
    try:
        reader = pypdf.PdfReader(str(pdf_path))
    except Exception as exc:  # noqa: BLE001 -- a real parse failure must be recorded, not raised
        stats["file_failure"] = f"{type(exc).__name__}: {exc}"
        return items, stats

    n_pages = len(reader.pages) if max_pages is None else min(max_pages, len(reader.pages))
    for page_idx in range(n_pages):
        try:
            text = reader.pages[page_idx].extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            stats["pages_failed"] += 1
            continue
        stats["pages_processed"] += 1
        for line in text.splitlines():
            stats["total_lines"] += 1
            if not _line_is_candidate_equation(line):
                continue
            stats["candidate_lines"] += 1
            location = f"page {page_idx + 1}"
            items.append(ReviewItem(
                review_id=stable_id("REVPDF", source_id, str(page_idx), line.strip()[:60]),
                equation_id=None, issue="PDF_TEXT_CANDIDATE_NOT_STRUCTURED",
                source_location=f"{source_id}:{location}", machine_proposal=line.strip(),
                unresolved_question="pypdf text extraction found a math-symbol-dense line; "
                                     "no reliable LaTeX/MathML recovery is possible from rendered "
                                     "PDF text alone, so this is NOT promoted to an equation "
                                     "record -- human review or a higher-quality source "
                                     "representation is required before this can be extracted "
                                     "as a structured equation (brief section VII).",
            ))
    return items, stats
