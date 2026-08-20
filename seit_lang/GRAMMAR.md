# `.seit` language grammar — Phase 1 (Language Kernel)

Status: **working definition for Phase 1, not canonical.** This grammar is
deliberately minimal — it covers exactly the keyword set the governing
brief specified for Phase 1, plus one documented extension (`report`)
needed to make the brief's own Phase 16 milestone example parse. Later
phases (2–16) are expected to extend this grammar (generic type
parameters, richer expressions, block bodies for `operator`, etc.); when
they do, this file is the place those extensions get documented, and
existing productions are extended, not silently reinterpreted.

## Lexical grammar

Tokens, in the order the lexer tries them:

```
COMMENT     := "#" any-char-except-newline* | "//" any-char-except-newline*   (discarded)
WHITESPACE  := (' ' | '\t' | '\r' | '\n')+                                     (discarded)
STRING      := '"' ( any-char-except-'"' | '\\"' )* '"'
NUMBER      := digit+ ('.' digit+)?
IDENT       := (alpha | '_') (alnum | '_')*
```

Keywords (reserved; matched as `IDENT` first, then looked up in the
keyword table — this is what makes `variable`, `derive`, etc. keywords
rather than ordinary identifiers):

```
module primitive variable constant operator equation definition
assumption dependency derive calculate verify theorem lemma audit
status provenance output report
```

`report` is not in the brief's Phase 1 keyword list (module, primitive,
variable, constant, operator, equation, definition, assumption,
dependency, derive, calculate, verify, theorem, lemma, audit, status,
provenance, output) but the brief's own Phase 16 example program
(`spectral_test.seit`) ends with a bare `report;` statement. It is added
here as a zero-argument statement so that example parses; it is exactly
as provisional as every other production in this file.

Punctuation/operators:

```
";" ":" "," "(" ")" "=" "==" "!=" "+" "-" "*" "/" "->"
```

## Syntactic grammar (EBNF)

```ebnf
program         := statement* ;

statement       := module_decl
                  | variable_decl
                  | constant_decl
                  | primitive_decl
                  | operator_decl
                  | equation_decl
                  | definition_decl
                  | assumption_decl
                  | dependency_decl
                  | derive_stmt
                  | calculate_stmt
                  | verify_stmt
                  | theorem_decl
                  | lemma_decl
                  | audit_stmt
                  | status_stmt
                  | provenance_stmt
                  | output_stmt
                  | report_stmt ;

module_decl     := "module" IDENT ";" ;
variable_decl   := "variable" IDENT ":" type_expr ";" ;
constant_decl   := "constant" IDENT ":" type_expr "=" expr ";" ;
primitive_decl  := "primitive" IDENT ":" type_expr ";" ;
operator_decl   := "operator" IDENT "(" param_list? ")" ":" type_expr ";" ;
equation_decl   := "equation" IDENT ":" expr ";" ;
definition_decl := "definition" IDENT "=" expr ";" ;
assumption_decl := "assumption" IDENT ":" expr ";" ;
dependency_decl := "dependency" IDENT "->" IDENT ("," IDENT)* ";" ;

derive_stmt     := "derive" (IDENT "=")? expr ";" ;
calculate_stmt  := "calculate" (IDENT "=")? expr ";" ;
verify_stmt     := "verify" expr ";" ;
theorem_decl    := "theorem" IDENT ":" expr ";" ;
lemma_decl      := "lemma" IDENT ":" expr ";" ;
audit_stmt      := "audit" IDENT ";" ;
status_stmt     := "status" IDENT "=" IDENT ";" ;
provenance_stmt := "provenance" IDENT "=" STRING ";" ;
output_stmt     := "output" IDENT ";" ;
report_stmt     := "report" ";" ;

param_list      := param ("," param)* ;
param           := IDENT ":" type_expr ;

type_expr       := IDENT ;   -- e.g. IncidenceMatrix, Laplacian (Phase 2
                                 gives this production real semantic
                                 content; Phase 1 accepts any identifier)

expr            := equality ;
equality        := additive (("=" | "==" | "!=") additive)* ;
additive        := term (("+" | "-") term)* ;
term            := unary (("*" | "/") unary)* ;
unary           := "-" unary | postfix ;
postfix         := primary ("(" arg_list? ")")* ;
arg_list        := expr ("," expr)* ;
primary         := NUMBER | STRING | IDENT | "(" expr ")" ;
```

`derive`/`calculate` allow either a bound form (`derive L = B *
transpose(B);`) or a bare-expression form (`derive spectrum(L);`, matching
the milestone example) — both appear in the brief's own Phase 16 example
program, so both are accepted rather than picking one and rejecting the
other.

## Worked example (the brief's Phase 16 milestone program)

```seit
module spectral_test;
variable B: IncidenceMatrix;
variable L: Laplacian;
derive L = B * transpose(B);
verify symmetric(L);
verify positive_semidefinite(L);
derive spectrum(L);
derive heat_kernel(L, beta);
report;
```

Every line above is a `statement` production; `B * transpose(B)` exercises
`term` → `postfix` with a nested call; `symmetric(L)` and
`positive_semidefinite(L)` exercise `verify_stmt` with a call expression.

## What Phase 1 deliberately leaves out

- No block bodies (`{ ... }`) for `operator` — Phase 1 operators are
  declarations (name/params/return type) only; giving them executable
  bodies is physics-kernel-binding work (Phase 5+), not language kernel.
- No generic/parametric types (`Matrix<3,3>`) — `type_expr` is a bare
  identifier; Phase 2's semantic type system decides what identifiers are
  valid types and what parameters (if any) they carry.
- No user-defined control flow (`if`, loops) — nothing in the governing
  brief's Phase 1–16 list calls for one, and derivations in this project
  are DAGs of declarative statements, not imperative procedures.

These are not bugs; they are exactly the "do NOT assume this exact syntax
is canonical" scope boundary the brief itself draws for Phase 1.
