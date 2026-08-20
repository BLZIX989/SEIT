"""Real, deterministic LaTeX token-occurrence scanner (brief section VI/
IX/XI: conservative, pattern-based extraction -- not semantic
interpretation, not a full LaTeX parser). Detects candidate operator and
variable/symbol occurrences in a LaTeX string, and candidate bracket
relations (commutator/anticommutator/Poisson-bracket-shaped expressions).

A pure-regex first version was tried and discarded during this phase
after it leaked individual letters out of command names against real
string-theory equation LaTeX (e.g. "\\dot{\\vec{x}}" spuriously producing
symbol occurrences "d", "o", "t"), and a masking-based regex fix still
corrupted composite symbols like "g_{\\alpha\\beta}" into "g_{ }" because
masking Greek letters before symbol matching blanked out subscript
content that should have stayed attached to its base letter. Both were
real, empirically-found bugs, not hypotheticals -- fixed here with a
small hand-rolled scanner that walks the string once, left to right,
resolving nesting explicitly (balanced braces) instead of trying to
force nested LaTeX into a single regex.
"""
from __future__ import annotations

import re

from scientific_corpus.extraction.schema import OperatorOccurrence, SymbolOccurrence, stable_id

_OPERATOR_COMMANDS = {
    "operatorname", "partial", "nabla", "Box", "Delta", "int", "sum",
    "exp", "log", "det", "sqrt", "star", "delta",
}
_ACCENT_COMMANDS = {"mathcal", "hat", "dot", "bar", "tilde", "vec", "widetilde", "widehat"}
_GREEK_COMMANDS = set((
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu "
    "xi omicron pi rho sigma tau upsilon phi chi psi omega "
    "Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega"
).split())
# delta and Delta appear in both operator and greek lists depending on
# context (Kronecker/variation vs. index) -- operator list wins, since
# \delta/\Delta occurring bare are far more often used as operators in
# this corpus's physics content; this is a documented heuristic
# tie-break, not a claim of semantic certainty.

_COMMAND_NAME = re.compile(r"\\([A-Za-z]+)")
_SUBSCRIPT_AFTER_CLOSE = re.compile(r"\s*(_\{[A-Za-z]+\}|_[A-Za-z]+)?\s*=\s*")


def _matching_brace(text: str, open_pos: int) -> int:
    """`text[open_pos]` must be '{'. Returns the index of its matching
    '}' (nesting-aware), or len(text) if unbalanced."""
    depth = 0
    i = open_pos
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text)


def _consume_script(text: str, pos: int) -> int:
    """`text[pos]` is '_' or '^'. Returns the end index just past the
    script's content (a braced group, or a single following atom -- a
    bare char or one more backslash command)."""
    i = pos + 1
    if i >= len(text):
        return pos + 1
    if text[i] == "{":
        return _matching_brace(text, i) + 1
    m = _COMMAND_NAME.match(text, i)
    if m:
        return m.end()
    return i + 1


def _consume_scripts(text: str, pos: int) -> int:
    i = pos
    while i < len(text) and text[i] in "_^":
        i = _consume_script(text, i)
    return i


def _tokenize(latex: str) -> list[tuple[int, int, str, str]]:
    """One left-to-right pass. Returns (start, end, literal, kind) for
    every detected token, kind in {"operator", "greek_index", "wrapped",
    "bare_symbol"}. Unknown commands (not in any curated list) are
    consumed (so their letters can never leak as spurious bare-symbol
    fragments) but not reported as tokens at all -- honest exclusion
    rather than a fabricated guess at their meaning."""
    tokens: list[tuple[int, int, str, str]] = []
    i = 0
    n = len(latex)
    while i < n:
        ch = latex[i]
        if ch == "\\":
            m = _COMMAND_NAME.match(latex, i)
            if not m:
                i += 1
                continue
            name = m.group(1)
            end = m.end()
            if name in _ACCENT_COMMANDS:
                arg_start = end
                while arg_start < n and latex[arg_start] == " ":
                    arg_start += 1  # e.g. "\hat x" -- skip the space before the argument
                if arg_start < n and latex[arg_start] == "{":
                    arg_end = _matching_brace(latex, arg_start) + 1
                elif arg_start < n:
                    cm = _COMMAND_NAME.match(latex, arg_start)
                    arg_end = cm.end() if cm else arg_start + 1
                else:
                    arg_end = arg_start
                arg_end = _consume_scripts(latex, arg_end)
                tokens.append((i, arg_end, latex[i:arg_end], "wrapped"))
                i = arg_end
            elif name in _OPERATOR_COMMANDS:
                op_end = end
                if name == "operatorname" and op_end < n and latex[op_end] == "{":
                    op_end = _matching_brace(latex, op_end) + 1
                op_end = _consume_scripts(latex, op_end)
                tokens.append((i, op_end, latex[i:op_end], "operator"))
                i = op_end
            elif name in _GREEK_COMMANDS:
                g_end = _consume_scripts(latex, end)
                tokens.append((i, g_end, latex[i:g_end], "greek_index"))
                i = g_end
            else:
                i = end  # unknown command: consumed, not reported
        elif ch.isalpha():
            end = _consume_scripts(latex, i + 1)
            tokens.append((i, end, latex[i:end], "bare_symbol"))
            i = end
        else:
            i += 1
    return tokens


def extract_symbols(latex: str, equation_id: str, source_id: str,
                     source_location: str, extraction_method: str) -> list[SymbolOccurrence]:
    """One SymbolOccurrence per distinct literal symbol within this
    equation (brief section X: never merged across equation_id)."""
    seen: dict[str, SymbolOccurrence] = {}
    for _start, _end, literal, kind in _tokenize(latex):
        if kind == "operator" or literal in seen:
            continue
        mtype = "INDEX_OR_SCALAR_UNRESOLVED" if kind == "greek_index" else "UNRESOLVED"
        vid = stable_id("SCIVAR", source_id, equation_id, literal)
        seen[literal] = SymbolOccurrence(
            variable_id=vid, equation_id=equation_id, literal_symbol=literal,
            local_definition="UNKNOWN", role="VARIABLE_TOKEN", mathematical_type=mtype,
            source_id=source_id, source_location=source_location,
            extraction_method=extraction_method, confidence="TOKENIZER_HEURISTIC",
        )
    return list(seen.values())


def extract_operators(latex: str, equation_id: str, source_id: str,
                       source_location: str, extraction_method: str) -> list[OperatorOccurrence]:
    seen: dict[str, OperatorOccurrence] = {}
    for _start, _end, literal, kind in _tokenize(latex):
        if kind != "operator" or literal in seen:
            continue
        oid = stable_id("SCIOPX", source_id, equation_id, literal)
        seen[literal] = OperatorOccurrence(
            operator_id=oid, equation_id=equation_id, symbol=literal,
            source_id=source_id, source_location=source_location,
            definition="UNKNOWN", extraction_method=extraction_method,
            confidence="TOKENIZER_HEURISTIC",
        )
    return list(seen.values())


def _top_level_comma_split(content: str) -> list[str] | None:
    """Splits `content` on commas that are NOT nested inside (), {}, or
    []. Returns None if there isn't exactly one such comma -- a
    commutator/anticommutator/bracket relation with zero or 2+ top-level
    arguments doesn't match the [A,B]-shape this function looks for, and
    guessing which comma is "the" separator would risk a wrong split
    (this was a real bug: a naive first-comma regex split
    "X^\\mu(\\sigma,\\tau)" at the comma INSIDE the parentheses instead
    of treating it as one argument)."""
    depth = 0
    split_at: list[int] = []
    for i, ch in enumerate(content):
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        elif ch == "," and depth == 0:
            split_at.append(i)
    if len(split_at) != 1:
        return None
    i = split_at[0]
    return [content[:i].strip(), content[i + 1:].strip()]


def extract_bracket_relations(latex: str) -> list[dict]:
    """Returns raw match dicts -- caller assigns relation_type using
    PB-subscript vs. bracket-shape disambiguation (needs equation-level
    context this pure function doesn't have). Only reports a relation
    where the bracket content splits into exactly two top-level
    (paren/brace/bracket-depth-aware) comma-separated arguments followed
    by "=" -- anything else is left undetected rather than guessed at."""
    results = []
    n = len(latex)
    i = 0
    while i < n:
        is_brace = latex.startswith("\\{", i)
        is_square = latex[i] == "["
        if not (is_brace or is_square):
            i += 1
            continue
        open_tok = "\\{" if is_brace else "["
        open_len = len(open_tok)
        content_start = i + open_len
        depth = 1
        j = content_start
        while j < n and depth > 0:
            if latex.startswith("\\{", j):
                depth += 1
                j += 2
                continue
            if latex.startswith("\\}", j):
                depth -= 1
                if depth == 0:
                    break
                j += 2
                continue
            if is_square and latex[j] == "[":
                depth += 1
            elif is_square and latex[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0 or j >= n:
            i += 1
            continue  # unbalanced -- not a relation, skip
        content = latex[content_start:j]
        close_end = j + (2 if is_brace else 1)

        parts = _top_level_comma_split(content)
        if parts is None:
            i = close_end
            continue
        m = _SUBSCRIPT_AFTER_CLOSE.match(latex, close_end)
        if not m:
            i = close_end
            continue
        tail_start = m.end()
        results.append({
            "open": open_tok, "lhs": parts[0], "rhs": parts[1],
            "subscript": m.group(1) or "",
            "matched_text": latex[i:tail_start],
            "rhs_expr_snippet": latex[tail_start:tail_start + 40],
        })
        i = tail_start
    return results
