"""Offline tests for scientific_corpus/extraction/tokenizer.py. Several
of these are regression tests for real bugs found by running the
tokenizer against real string-theory equation LaTeX during Phase 14 --
not hypothetical edge cases.
"""
from __future__ import annotations

from scientific_corpus.extraction.tokenizer import (
    extract_bracket_relations, extract_operators, extract_symbols,
)


def _symbols(latex):
    return {s.literal_symbol for s in extract_symbols(latex, "EQ-1", "SRC-1", "loc", "LATEX_SOURCE")}


def _operators(latex):
    return {o.symbol for o in extract_operators(latex, "EQ-1", "SRC-1", "loc", "LATEX_SOURCE")}


def test_composite_subscript_symbol_not_fragmented():
    """g_{\\alpha\\beta} must be ONE symbol, not three (g, alpha, beta)."""
    syms = _symbols(r"g_{\alpha\beta}=2f(\sigma)")
    assert r"g_{\alpha\beta}" in syms
    assert "g" not in syms
    assert r"\alpha" not in syms


def test_einstein_equation_symbols_and_no_leakage():
    syms = _symbols(r"G_{\mu\nu} + \Lambda g_{\mu\nu} = 8\pi G T_{\mu\nu}")
    assert syms == {r"G_{\mu\nu}", r"g_{\mu\nu}", r"T_{\mu\nu}", "G", r"\Lambda", r"\pi"}


def test_nested_accent_command_does_not_leak_letters():
    """Regression: \\dot{\\vec{x}} previously leaked "d", "o", "t" as
    spurious bare-symbol fragments from inside the command name."""
    syms = _symbols(r"\dot{\vec{x}}\cdot\dot{\vec{x}}")
    assert syms == {r"\dot{\vec{x}}"}


def test_unbraced_accent_argument_with_space_is_captured_whole():
    """Regression: "\\hat x" (space before the argument, no braces) was
    previously split into a bare "\\hat " token plus a separate "x"."""
    syms = _symbols(r"[\hat x,\hat p] = i\hbar")
    assert r"\hat x" in syms
    assert r"\hat p" in syms
    assert "x" not in syms
    assert "p" not in syms


def test_operator_with_index_captured_as_one_token():
    ops = _operators(r"\partial_\alpha X\cdot\partial_\beta X")
    assert ops == {r"\partial_\alpha", r"\partial_\beta"}


def test_greek_letters_are_not_classified_as_operators():
    """A real bug found this phase: an earlier version tagged every
    Greek letter as an "operator" -- but \\mu, \\nu, \\alpha etc. are
    used as tensor indices throughout this corpus's actual equations,
    not as operators."""
    ops = _operators(r"g_{\alpha\beta}=2f(\sigma)\,\partial_\alpha X\cdot\partial_\beta X")
    for greek in (r"\alpha", r"\beta", r"\sigma"):
        assert greek not in ops


def test_clifford_anticommutator_symbols():
    syms = _symbols(r"\{\gamma^\mu,\gamma^\nu\} = 2g^{\mu\nu}I")
    assert r"\gamma^\mu" in syms
    assert r"\gamma^\nu" in syms
    assert r"g^{\mu\nu}" in syms
    assert "I" in syms


def test_extract_bracket_relations_captures_commutator_shape():
    rels = extract_bracket_relations(r"[\hat x,\hat p] = i\hbar")
    assert len(rels) == 1
    assert rels[0]["open"] == "["
    assert rels[0]["lhs"] == r"\hat x"
    assert rels[0]["rhs"] == r"\hat p"
    assert rels[0]["subscript"] == ""


def test_extract_bracket_relations_handles_nested_commas_in_arguments():
    """Regression: a naive first-comma split would previously cut
    "X^\\mu(\\sigma,\\tau)" at the comma INSIDE the parentheses instead of
    treating the whole parenthesized expression as one argument."""
    rels = extract_bracket_relations(
        r"\{X^\mu(\sigma,\tau),\dot X^\nu(\sigma',\tau)\}_{PB}=\frac{1}{T}\delta"
    )
    assert len(rels) == 1
    assert rels[0]["lhs"] == r"X^\mu(\sigma,\tau)"
    assert rels[0]["rhs"] == r"\dot X^\nu(\sigma',\tau)"
    assert rels[0]["subscript"] == "_{PB}"


def test_extract_bracket_relations_distinguishes_poisson_bracket_subscript():
    """A brace-relation with an explicit _{PB} subscript must be
    distinguishable from a plain anticommutator -- never inferred as a
    commutator merely because brackets are present (brief section XII)."""
    rels = extract_bracket_relations(r"\{L_m,L_n\}_{PB}=-i(m-n)L_{m+n}")
    assert len(rels) == 1
    assert rels[0]["subscript"] == "_{PB}"


def test_symbol_occurrences_never_merge_across_equations():
    from scientific_corpus.extraction.tokenizer import extract_symbols
    a = extract_symbols("G", "EQ-A", "SRC-1", "loc", "LATEX_SOURCE")
    b = extract_symbols("G", "EQ-B", "SRC-1", "loc", "LATEX_SOURCE")
    assert a[0].variable_id != b[0].variable_id


def test_unknown_macro_is_silently_excluded_not_guessed():
    """A macro outside every curated list (operator/accent/greek) must
    never be reported as a symbol or operator -- it is consumed without
    being reported, rather than the tokenizer guessing at its meaning."""
    syms = _symbols(r"\somecustommacro{X} + Y")
    assert "Y" in syms
    assert not any("somecustommacro" in s for s in syms)


def test_deterministic_repeated_extraction():
    latex = r"G_{\mu\nu} + \Lambda g_{\mu\nu} = 8\pi G T_{\mu\nu}"
    a = extract_symbols(latex, "EQ-1", "SRC-1", "loc", "LATEX_SOURCE")
    b = extract_symbols(latex, "EQ-1", "SRC-1", "loc", "LATEX_SOURCE")
    assert [s.to_dict() for s in a] == [s.to_dict() for s in b]
