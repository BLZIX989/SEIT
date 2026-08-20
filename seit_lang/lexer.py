"""Lexer for the `.seit` language (Phase 1 -- see GRAMMAR.md).

Hand-written, single-pass, no external parsing dependency -- consistent
with the rest of this repo's compiler (compiler/ir, compiler/dependencies)
which is also plain, auditable Python.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # literals / names
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    # keywords
    MODULE = auto()
    PRIMITIVE = auto()
    VARIABLE = auto()
    CONSTANT = auto()
    OPERATOR = auto()
    EQUATION = auto()
    DEFINITION = auto()
    ASSUMPTION = auto()
    DEPENDENCY = auto()
    DERIVE = auto()
    CALCULATE = auto()
    VERIFY = auto()
    THEOREM = auto()
    LEMMA = auto()
    AUDIT = auto()
    STATUS = auto()
    PROVENANCE = auto()
    OUTPUT = auto()
    REPORT = auto()
    # punctuation / operators
    SEMICOLON = auto()
    COLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    ASSIGN = auto()      # =
    EQ = auto()           # ==
    NEQ = auto()          # !=
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ARROW = auto()        # ->
    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "module": TokenType.MODULE,
    "primitive": TokenType.PRIMITIVE,
    "variable": TokenType.VARIABLE,
    "constant": TokenType.CONSTANT,
    "operator": TokenType.OPERATOR,
    "equation": TokenType.EQUATION,
    "definition": TokenType.DEFINITION,
    "assumption": TokenType.ASSUMPTION,
    "dependency": TokenType.DEPENDENCY,
    "derive": TokenType.DERIVE,
    "calculate": TokenType.CALCULATE,
    "verify": TokenType.VERIFY,
    "theorem": TokenType.THEOREM,
    "lemma": TokenType.LEMMA,
    "audit": TokenType.AUDIT,
    "status": TokenType.STATUS,
    "provenance": TokenType.PROVENANCE,
    "output": TokenType.OUTPUT,
    "report": TokenType.REPORT,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class LexError(SyntaxError):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"{message} (line {line}, column {column})")
        self.line = line
        self.column = column


_SINGLE_CHAR = {
    ";": TokenType.SEMICOLON,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,  # overridden below when followed by '>'
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
}


def tokenize(source: str) -> list[Token]:
    """Tokenize `.seit` source into a flat token list, ending with EOF.
    Raises LexError on any character that cannot start a valid token."""
    tokens: list[Token] = []
    i = 0
    n = len(source)
    line = 1
    col = 1

    def advance(k: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(k):
            if i < n and source[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        ch = source[i]

        if ch in " \t\r\n":
            advance()
            continue

        if ch == "#" or (ch == "/" and i + 1 < n and source[i + 1] == "/"):
            while i < n and source[i] != "\n":
                advance()
            continue

        start_line, start_col = line, col

        if ch == '"':
            j = i + 1
            buf = []
            while j < n and source[j] != '"':
                if source[j] == "\\" and j + 1 < n and source[j + 1] == '"':
                    buf.append('"')
                    j += 2
                    continue
                buf.append(source[j])
                j += 1
            if j >= n:
                raise LexError("unterminated string literal", start_line, start_col)
            advance(j - i + 1)
            tokens.append(Token(TokenType.STRING, "".join(buf), start_line, start_col))
            continue

        if ch.isdigit():
            j = i
            while j < n and source[j].isdigit():
                j += 1
            if j < n and source[j] == "." and j + 1 < n and source[j + 1].isdigit():
                j += 1
                while j < n and source[j].isdigit():
                    j += 1
            text = source[i:j]
            advance(j - i)
            tokens.append(Token(TokenType.NUMBER, text, start_line, start_col))
            continue

        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            text = source[i:j]
            advance(j - i)
            ttype = KEYWORDS.get(text, TokenType.IDENT)
            tokens.append(Token(ttype, text, start_line, start_col))
            continue

        if ch == "-" and i + 1 < n and source[i + 1] == ">":
            advance(2)
            tokens.append(Token(TokenType.ARROW, "->", start_line, start_col))
            continue

        if ch == "=" and i + 1 < n and source[i + 1] == "=":
            advance(2)
            tokens.append(Token(TokenType.EQ, "==", start_line, start_col))
            continue

        if ch == "=":
            advance()
            tokens.append(Token(TokenType.ASSIGN, "=", start_line, start_col))
            continue

        if ch == "!" and i + 1 < n and source[i + 1] == "=":
            advance(2)
            tokens.append(Token(TokenType.NEQ, "!=", start_line, start_col))
            continue

        if ch in _SINGLE_CHAR:
            advance()
            tokens.append(Token(_SINGLE_CHAR[ch], ch, start_line, start_col))
            continue

        raise LexError(f"unexpected character {ch!r}", start_line, start_col)

    tokens.append(Token(TokenType.EOF, "", line, col))
    return tokens
