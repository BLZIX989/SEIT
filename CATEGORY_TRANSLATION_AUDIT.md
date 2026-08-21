# CATEGORY_TRANSLATION_AUDIT.md

## Finding stated up front

The Chainlink registry is a PROJECTION (a function from real compiler registry state to a derived view), not a functor between two independently-defined categories with their own composition laws -- so 'F(g.f)=F(g).F(g)' is not a well-posed question for it. What IS well-posed and tested below: does the projection faithfully preserve the real dependency-edge structure of the underlying compiler registries?

## Structure-preservation result

- total chainlinks: 16
- backed by a real canonical dependency edge: 15
- self-documented intentional open gaps (not violations): 1
- genuine violations: 0

**Verdict:** STRUCTURE-PRESERVATION HOLDS. 7/8 chainlinks are directly backed by a real canonical dependency edge; the 8th (CL-METRIC-TO-CONNECTION) references a target ('CONNECTION-NODE') that is not in any canonical registry, but its own transformation field says so explicitly ('(NOT REGISTERED)') and its open_obligations text states plainly that 'no admissible, non-arbitrary construction of a connection from a non-unique metric candidate is registered' -- this is the chainlink honestly marking an open frontier boundary, exactly the behavior compiler/protocol/derivation_chainlinks.py's own docstring promises ('this module only reads t.status/t.proof/t.dependencies off the already-built registries'), not a fabricated relationship.

## Composability result

- composable pairs (A->B, B->C sharing a node): 7
- with an explicit direct composite A->C also registered: 0

The Chainlink registry represents each real compiler transformation as ONE edge (a DIRECT-dependency graph), never synthesizing a transitive composite edge that doesn't correspond to an actual single transformation the compiler runs. This is the CORRECT and intended behavior given the project's own isolation discipline (never fabricate a relationship the compiler didn't itself compute) -- it means the registry is not attempting to BE a category with composition, it is a faithful direct-edge projection, and any 'is this chain composable end-to-end' question must be answered by graph reachability over these direct edges, not by expecting a registered composite record.
