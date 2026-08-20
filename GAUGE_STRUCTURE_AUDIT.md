# GAUGE_STRUCTURE_AUDIT.md

## Existing results (unchanged)

- H4 intersection-via-triality claim: **FALSIFIED** (rank(G2)=2 < rank(SM)=4).
- H4 direct-product claim (Aut(O)xSpin(8)): **UNCONSTRUCTED**, not falsified (rank(G2)+rank(Spin(8))=6 >= rank(SM)=4).

## New: sub-embedding checks (H4B)

### SU(3) subset G2 (maximal subgroup, standard external Lie theory)
- rank(SU(3))=2 <= rank(G2)=2: CONSISTENT
- dim(G2)-dim(SU(3)) = 14-8 = 6, matching the known dimension of the coset space G2/SU(3) = S^6 (the 6-sphere) -- consistent with the standard fact, not an independent proof of it (that requires the actual root-system embedding, which is standard but not reproduced here).
- status: **CONDITIONALLY SUPPORTED -- real, standard mathematics; NOT independently re-derived by this project, cited as established external fact.**

### SU(2)xU(1) subset Spin(8)
- rank(SU(2)xU(1))=2 <= rank(Spin(8))=4: NECESSARY CONDITION SATISFIED
- dim(SU(2)xU(1))=4 <= dim(Spin(8))=28: NECESSARY CONDITION SATISFIED
- status: **UNRESOLVED -- rank and dimension are NECESSARY, not sufficient, conditions for subgroup embedding. Spin(8) does contain many rank-2 subgroups (e.g. SU(2)xSU(2)xSU(2)xSU(2) is a maximal-rank-4 subgroup via the D4 root system; SU(2)xU(1) embeds inside various of Spin(8)'s maximal subgroups by further restriction), so infeasibility is NOT the finding here -- but no SPECIFIC embedding tied to this project's actual spectral/graph construction has been given anywhere in the corpus, so 'feasible in principle' must not be read as 'constructed'.**

## The specific gap that matters for THIS project (H4C)

A specific graph construction (topology, size, edge-weight rule) that the corpus asserts represents 'the physical vacuum state' or equivalent, whose low-lying Laplacian spectrum is claimed to exhibit degeneracy (3,2,1). No such construction rule exists anywhere in the accessible corpus -- Vol.4 Ch.23 itself states this is 'the central open question for SEIT's derivation of the Standard Model gauge structure' and marks it [Conjecture]. Once such a graph is specified, this IS directly computable with the compiler's existing eigh()-based spectral backend (compiler/backends/spectral.py) -- eigenvalue multiplicities are a standard, cheap linear-algebra computation, not a conceptual obstacle.
