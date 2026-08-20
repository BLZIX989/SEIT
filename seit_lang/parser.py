"""Recursive-descent parser for the `.seit` language (Phase 1 -- see
GRAMMAR.md). Consumes the token stream from seit_lang.lexer.tokenize and
produces a seit_lang.ast_nodes.Program.
"""
from __future__ import annotations

from . import ast_nodes as ast
from .lexer import Token, TokenType, tokenize


class ParseError(SyntaxError):
    def __init__(self, message: str, token: Token):
        super().__init__(f"{message} (line {token.line}, column {token.column}, "
                          f"got {token.type.name} {token.value!r})")
        self.token = token


_DECL_KEYWORD_TYPES = {
    TokenType.MODULE, TokenType.PRIMITIVE, TokenType.VARIABLE, TokenType.CONSTANT,
    TokenType.OPERATOR, TokenType.EQUATION, TokenType.DEFINITION, TokenType.ASSUMPTION,
    TokenType.DEPENDENCY, TokenType.DERIVE, TokenType.CALCULATE, TokenType.VERIFY,
    TokenType.THEOREM, TokenType.LEMMA, TokenType.AUDIT, TokenType.STATUS,
    TokenType.PROVENANCE, TokenType.OUTPUT, TokenType.REPORT,
}

_BINARY_TOKENS = {
    TokenType.PLUS: "+", TokenType.MINUS: "-", TokenType.STAR: "*", TokenType.SLASH: "/",
    TokenType.ASSIGN: "=", TokenType.EQ: "==", TokenType.NEQ: "!=",
}
_ADDITIVE = {TokenType.PLUS, TokenType.MINUS}
_TERM = {TokenType.STAR, TokenType.SLASH}
_EQUALITY = {TokenType.ASSIGN, TokenType.EQ, TokenType.NEQ}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # -- token stream helpers --

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def check(self, ttype: TokenType) -> bool:
        return self.current.type == ttype

    def expect(self, ttype: TokenType) -> Token:
        if not self.check(ttype):
            raise ParseError(f"expected {ttype.name}", self.current)
        return self.advance()

    # -- entry point --

    def parse_program(self) -> ast.Program:
        start = self.current
        statements: list[ast.Statement] = []
        while not self.check(TokenType.EOF):
            statements.append(self.parse_statement())
        return ast.Program(line=start.line, column=start.column, statements=statements)

    # -- statements --

    def parse_statement(self) -> ast.Statement:
        tok = self.current
        dispatch = {
            TokenType.MODULE: self._parse_module,
            TokenType.VARIABLE: self._parse_variable,
            TokenType.CONSTANT: self._parse_constant,
            TokenType.PRIMITIVE: self._parse_primitive,
            TokenType.OPERATOR: self._parse_operator,
            TokenType.EQUATION: self._parse_equation,
            TokenType.DEFINITION: self._parse_definition,
            TokenType.ASSUMPTION: self._parse_assumption,
            TokenType.DEPENDENCY: self._parse_dependency,
            TokenType.DERIVE: lambda: self._parse_derive_or_calculate(ast.DeriveStmt, TokenType.DERIVE),
            TokenType.CALCULATE: lambda: self._parse_derive_or_calculate(ast.CalculateStmt, TokenType.CALCULATE),
            TokenType.VERIFY: self._parse_verify,
            TokenType.THEOREM: self._parse_theorem,
            TokenType.LEMMA: self._parse_lemma,
            TokenType.AUDIT: self._parse_audit,
            TokenType.STATUS: self._parse_status,
            TokenType.PROVENANCE: self._parse_provenance,
            TokenType.OUTPUT: self._parse_output,
            TokenType.REPORT: self._parse_report,
        }
        handler = dispatch.get(tok.type)
        if handler is None:
            raise ParseError("expected a statement", tok)
        return handler()

    def _parse_module(self) -> ast.ModuleDecl:
        tok = self.expect(TokenType.MODULE)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.SEMICOLON)
        return ast.ModuleDecl(line=tok.line, column=tok.column, name=name)

    def _parse_type_expr(self) -> ast.TypeExpr:
        tok = self.expect(TokenType.IDENT)
        return ast.TypeExpr(line=tok.line, column=tok.column, name=tok.value)

    def _parse_variable(self) -> ast.VariableDecl:
        tok = self.expect(TokenType.VARIABLE)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        type_ = self._parse_type_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.VariableDecl(line=tok.line, column=tok.column, name=name, type=type_)

    def _parse_constant(self) -> ast.ConstantDecl:
        tok = self.expect(TokenType.CONSTANT)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        type_ = self._parse_type_expr()
        self.expect(TokenType.ASSIGN)
        value = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.ConstantDecl(line=tok.line, column=tok.column, name=name, type=type_, value=value)

    def _parse_primitive(self) -> ast.PrimitiveDecl:
        tok = self.expect(TokenType.PRIMITIVE)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        type_ = self._parse_type_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.PrimitiveDecl(line=tok.line, column=tok.column, name=name, type=type_)

    def _parse_operator(self) -> ast.OperatorDecl:
        tok = self.expect(TokenType.OPERATOR)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LPAREN)
        params: list[ast.Param] = []
        if not self.check(TokenType.RPAREN):
            params.append(self._parse_param())
            while self.check(TokenType.COMMA):
                self.advance()
                params.append(self._parse_param())
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        return_type = self._parse_type_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.OperatorDecl(line=tok.line, column=tok.column, name=name,
                                 params=params, return_type=return_type)

    def _parse_param(self) -> ast.Param:
        tok = self.expect(TokenType.IDENT)
        self.expect(TokenType.COLON)
        type_ = self._parse_type_expr()
        return ast.Param(line=tok.line, column=tok.column, name=tok.value, type=type_)

    def _parse_equation(self) -> ast.EquationDecl:
        tok = self.expect(TokenType.EQUATION)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.EquationDecl(line=tok.line, column=tok.column, name=name, expr=expr)

    def _parse_definition(self) -> ast.DefinitionDecl:
        tok = self.expect(TokenType.DEFINITION)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.ASSIGN)
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.DefinitionDecl(line=tok.line, column=tok.column, name=name, expr=expr)

    def _parse_assumption(self) -> ast.AssumptionDecl:
        tok = self.expect(TokenType.ASSUMPTION)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.AssumptionDecl(line=tok.line, column=tok.column, name=name, expr=expr)

    def _parse_dependency(self) -> ast.DependencyDecl:
        tok = self.expect(TokenType.DEPENDENCY)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.ARROW)
        deps = [self.expect(TokenType.IDENT).value]
        while self.check(TokenType.COMMA):
            self.advance()
            deps.append(self.expect(TokenType.IDENT).value)
        self.expect(TokenType.SEMICOLON)
        return ast.DependencyDecl(line=tok.line, column=tok.column, name=name, depends_on=deps)

    def _parse_derive_or_calculate(self, node_cls, kw_type: TokenType):
        tok = self.expect(kw_type)
        target = None
        # Bound form `derive L = expr;` vs bare form `derive spectrum(L);`:
        # only IDENT "=" is the bound form -- anything else (a call, a
        # number, etc.) is the bare-expression form.
        if self.check(TokenType.IDENT) and self.tokens[self.pos + 1].type == TokenType.ASSIGN:
            target = self.advance().value
            self.expect(TokenType.ASSIGN)
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return node_cls(line=tok.line, column=tok.column, target=target, expr=expr)

    def _parse_verify(self) -> ast.VerifyStmt:
        tok = self.expect(TokenType.VERIFY)
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.VerifyStmt(line=tok.line, column=tok.column, expr=expr)

    def _parse_theorem(self) -> ast.TheoremDecl:
        tok = self.expect(TokenType.THEOREM)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.TheoremDecl(line=tok.line, column=tok.column, name=name, expr=expr)

    def _parse_lemma(self) -> ast.LemmaDecl:
        tok = self.expect(TokenType.LEMMA)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ast.LemmaDecl(line=tok.line, column=tok.column, name=name, expr=expr)

    def _parse_audit(self) -> ast.AuditStmt:
        tok = self.expect(TokenType.AUDIT)
        target = self.expect(TokenType.IDENT).value
        self.expect(TokenType.SEMICOLON)
        return ast.AuditStmt(line=tok.line, column=tok.column, target=target)

    def _parse_status(self) -> ast.StatusStmt:
        tok = self.expect(TokenType.STATUS)
        target = self.expect(TokenType.IDENT).value
        self.expect(TokenType.ASSIGN)
        value = self.expect(TokenType.IDENT).value
        self.expect(TokenType.SEMICOLON)
        return ast.StatusStmt(line=tok.line, column=tok.column, target=target, value=value)

    def _parse_provenance(self) -> ast.ProvenanceStmt:
        tok = self.expect(TokenType.PROVENANCE)
        target = self.expect(TokenType.IDENT).value
        self.expect(TokenType.ASSIGN)
        value = self.expect(TokenType.STRING).value
        self.expect(TokenType.SEMICOLON)
        return ast.ProvenanceStmt(line=tok.line, column=tok.column, target=target, value=value)

    def _parse_output(self) -> ast.OutputStmt:
        tok = self.expect(TokenType.OUTPUT)
        target = self.expect(TokenType.IDENT).value
        self.expect(TokenType.SEMICOLON)
        return ast.OutputStmt(line=tok.line, column=tok.column, target=target)

    def _parse_report(self) -> ast.ReportStmt:
        tok = self.expect(TokenType.REPORT)
        self.expect(TokenType.SEMICOLON)
        return ast.ReportStmt(line=tok.line, column=tok.column)

    # -- expressions (precedence climbing) --

    def parse_expr(self) -> ast.Expr:
        return self._parse_equality()

    def _parse_equality(self) -> ast.Expr:
        left = self._parse_additive()
        while self.current.type in _EQUALITY:
            op_tok = self.advance()
            right = self._parse_additive()
            left = ast.BinaryOp(line=op_tok.line, column=op_tok.column,
                                 op=_BINARY_TOKENS[op_tok.type], left=left, right=right)
        return left

    def _parse_additive(self) -> ast.Expr:
        left = self._parse_term()
        while self.current.type in _ADDITIVE:
            op_tok = self.advance()
            right = self._parse_term()
            left = ast.BinaryOp(line=op_tok.line, column=op_tok.column,
                                 op=_BINARY_TOKENS[op_tok.type], left=left, right=right)
        return left

    def _parse_term(self) -> ast.Expr:
        left = self._parse_unary()
        while self.current.type in _TERM:
            op_tok = self.advance()
            right = self._parse_unary()
            left = ast.BinaryOp(line=op_tok.line, column=op_tok.column,
                                 op=_BINARY_TOKENS[op_tok.type], left=left, right=right)
        return left

    def _parse_unary(self) -> ast.Expr:
        if self.check(TokenType.MINUS):
            tok = self.advance()
            operand = self._parse_unary()
            return ast.UnaryOp(line=tok.line, column=tok.column, op="-", operand=operand)
        return self._parse_postfix()

    def _parse_postfix(self) -> ast.Expr:
        expr = self._parse_primary()
        while self.check(TokenType.LPAREN):
            if not isinstance(expr, ast.Identifier):
                raise ParseError("only an identifier may be called as a function", self.current)
            lparen = self.advance()
            args: list[ast.Expr] = []
            if not self.check(TokenType.RPAREN):
                args.append(self.parse_expr())
                while self.check(TokenType.COMMA):
                    self.advance()
                    args.append(self.parse_expr())
            self.expect(TokenType.RPAREN)
            expr = ast.Call(line=lparen.line, column=lparen.column, callee=expr.name, args=args)
        return expr

    def _parse_primary(self) -> ast.Expr:
        tok = self.current
        if tok.type == TokenType.NUMBER:
            self.advance()
            return ast.NumberLit(line=tok.line, column=tok.column, value=float(tok.value))
        if tok.type == TokenType.STRING:
            self.advance()
            return ast.StringLit(line=tok.line, column=tok.column, value=tok.value)
        if tok.type == TokenType.IDENT:
            self.advance()
            return ast.Identifier(line=tok.line, column=tok.column, name=tok.value)
        if tok.type == TokenType.LPAREN:
            self.advance()
            inner = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return inner
        raise ParseError("expected an expression", tok)


def parse(source: str) -> ast.Program:
    """Tokenize and parse `.seit` source into a Program AST."""
    return Parser(tokenize(source)).parse_program()
