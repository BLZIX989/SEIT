"""Tests for seit_lang.lexer (Phase 1)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seit_lang.lexer import LexError, TokenType, tokenize


def _types(tokens):
    return [t.type for t in tokens]


def test_tokenizes_all_keywords():
    src = ("module primitive variable constant operator equation definition "
           "assumption dependency derive calculate verify theorem lemma audit "
           "status provenance output report")
    tokens = tokenize(src)
    expected = [
        TokenType.MODULE, TokenType.PRIMITIVE, TokenType.VARIABLE, TokenType.CONSTANT,
        TokenType.OPERATOR, TokenType.EQUATION, TokenType.DEFINITION, TokenType.ASSUMPTION,
        TokenType.DEPENDENCY, TokenType.DERIVE, TokenType.CALCULATE, TokenType.VERIFY,
        TokenType.THEOREM, TokenType.LEMMA, TokenType.AUDIT, TokenType.STATUS,
        TokenType.PROVENANCE, TokenType.OUTPUT, TokenType.REPORT, TokenType.EOF,
    ]
    assert _types(tokens) == expected


def test_identifier_not_confused_with_keyword_prefix():
    tokens = tokenize("variables")
    assert tokens[0].type == TokenType.IDENT
    assert tokens[0].value == "variables"


def test_punctuation_and_operators():
    tokens = tokenize("; : , ( ) = == != + - * / ->")
    assert _types(tokens) == [
        TokenType.SEMICOLON, TokenType.COLON, TokenType.COMMA, TokenType.LPAREN,
        TokenType.RPAREN, TokenType.ASSIGN, TokenType.EQ, TokenType.NEQ,
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
        TokenType.ARROW, TokenType.EOF,
    ]


def test_number_literals_int_and_float():
    tokens = tokenize("42 3.14")
    assert tokens[0].type == TokenType.NUMBER and tokens[0].value == "42"
    assert tokens[1].type == TokenType.NUMBER and tokens[1].value == "3.14"


def test_string_literal_with_escaped_quote():
    tokens = tokenize(r'"hello \"world\""')
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == 'hello "world"'


def test_line_comment_hash_and_slash_forms_are_discarded():
    tokens = tokenize("module m; # trailing comment\n// another\nvariable x: T;")
    assert _types(tokens) == [
        TokenType.MODULE, TokenType.IDENT, TokenType.SEMICOLON,
        TokenType.VARIABLE, TokenType.IDENT, TokenType.COLON, TokenType.IDENT,
        TokenType.SEMICOLON, TokenType.EOF,
    ]


def test_unterminated_string_raises_lex_error():
    with pytest.raises(LexError):
        tokenize('"unterminated')


def test_unexpected_character_raises_lex_error():
    with pytest.raises(LexError):
        tokenize("variable x: T; @")


def test_line_and_column_tracking_across_newlines():
    tokens = tokenize("module m;\nvariable x: T;")
    variable_tok = tokens[3]
    assert variable_tok.type == TokenType.VARIABLE
    assert variable_tok.line == 2
    assert variable_tok.column == 1


def test_tokenizes_milestone_fixture_program():
    fixture = (Path(__file__).parent / "fixtures" / "spectral_test.seit").read_text()
    tokens = tokenize(fixture)
    assert tokens[-1].type == TokenType.EOF
    assert TokenType.DERIVE in _types(tokens)
    assert TokenType.REPORT in _types(tokens)
