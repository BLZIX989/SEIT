# MASTER THEORY GAP REPORT

The exact remaining obstruction on each of the four branches this campaign targeted, stated as
precisely as the executed evidence supports.

## H1 — Selection closure: **definitional gap, not a missing proof**
**Obstruction:** `Mathset`, `Π(G)` (persistence functional), and `S(G)` (structural-cost
functional) have no implementation anywhere in `compiler/backends/*.py` or
`compiler/ir/forward_chain.py`. `G*=argmax_G Π(G)/S(G)` cannot be evaluated for well-posedness
because its domain and objective are not specified. **What would close this:** an explicit,
non-circular, representation-invariant definition of `Π` and `S` as computable functionals on a
precisely specified space of graphs, followed by an existence/uniqueness proof for the argmax
(or a proof that none exists). No such definition currently exists in this project's corpus or
literature crosswalk.

## H2 — Spectral-triple/Dirac closure: **structural locality failure**
**Obstruction:** `D+=sqrt(L)` is numerically dense (no exact zeros off-diagonal,
`D+_sparsity_strict=1.0`) with slow off-diagonal decay (row values 0.290/0.280/0.268 at
graph-distances 1/2/3), even for a sparse, local `L` (`L_sparsity=0.035`). A Dirac-type operator
in a spectral triple needs `[D,a]` bounded for `a` drawn from a *local* algebra — locality of
the underlying graph does not survive the operator square root. **What would close this:** a
different, genuinely local construction of a Dirac-type operator from graph data (not the naive
square root), together with a full check of the remaining Connes axioms (real structure `J` with
correct KO-dimension, grading, first-order condition, finiteness) for a fixed choice of algebra
`A` — none of which has been attempted for this project's actual `D+`.

## H3 — Discrete→continuum/geometry closure: **higher-mode instability survives two non-circular corrections**
**Obstruction:** modes 5-15 remain eigenvector-unstable (`subspace_cosine≈0.02`, near-orthogonal)
under both a tighter solver tolerance and a 2× bandwidth increase; only low modes [1,3] respond
to bandwidth. The one proposed fix with the right qualitative shape (a curvature-dependent
kernel correction) is circular as stated — it needs the very curvature the pipeline is trying to
derive. **What would close this:** either (a) an independent, non-circular estimate of local
curvature/geometry usable as a kernel input without assuming the answer, or (b) a theoretical
argument for why higher modes are expected not to converge at this sample-size regime and a
demonstration that they do converge at asymptotically larger N — neither is in hand.

## H4 — Gauge/internal algebra closure: **one specific route is impossible; the project's own route is unconstructed**
**Obstruction (falsified route):** the triality-fixed subgroup of Spin(8) is G2 (rank 2), and no
rank-2 compact Lie group can contain a rank-4 subgroup — SU(3)×SU(2)×U(1) (rank 4) can never sit
inside G2 under any embedding. This route is closed, permanently, by a general theorem, not by
absence of effort. **Obstruction (repository's own route, direct-product `Aut(octonions)×Spin(8)
⊇ SU(3)×SU(2)×U(1)`):** not ruled out by rank (6 ≥ 4), but zero construction exists anywhere in
this repository — no explicit embedding, no decomposition of the direct product's representation
theory, no uniqueness argument ruling out other candidate subgroups of the same rank. **What
would close this:** an actual embedding map `SU(3)×SU(2)×U(1) ↪ Aut(octonions)×Spin(8)`
constructed and verified (e.g. via explicit generators or a representation-theoretic
decomposition), plus an argument for why this particular embedding — and not some other
rank-compatible one — is the physically selected one (which reopens a version of the H1
selection problem).

## Cross-cutting observation
Three of the four obstructions (H1, and the "why this embedding" residual of H4) reduce to the
same underlying gap: this project has no working, non-circular *selection principle*. H2 and H3
are independent technical obstructions (operator locality; discrete-sampling convergence) that
would need to be solved even if selection were resolved. There is no evidence in this repository,
the historical corpus, or the two newly-inspected external xlsx workbooks (which independently
corroborate H1's and H4's open status on their own OPEN-labeled sheets — see
`MASTER_THEORY_AUDIT_REPORT.md` §3) that any of these four gaps has actually been closed anywhere.
