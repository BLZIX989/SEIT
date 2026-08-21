# DERIVATION_FRONTIER.md

Complete map of every mathematical arrow in the Delta -> Gamma -> G -> L -> Spec(L) -> Pi -> d(i,j) -> g_munu -> nabla -> Riemann -> Ricci -> scalar curvature -> Einstein tensor -> action -> Euler-Lagrange chain, classified per the brief's governing epistemic rule. Every status below traces to a specific computation in scientific_corpus/derivation/DERIVATION_RESULTS.json -- none is asserted.

| Arrow | Status | Evidence |
|---|---|---|
| Delta -> Gamma -> G -> L | DERIVED + COMPUTED | Already implemented (compiler/backends/graph_laplacian.py); re-verified here as the substrate for every other test in this phase. |
| L -> Spec(L) | COMPUTED | compiler/backends/spectral.py, real eigendecomposition, reused throughout this phase (mass_spectrum.py, dirac_candidates.py). |
| Spec(L) -> Pi (persistence sector) -> d(i,j) (diffusion distance) | COMPUTED, CONDITIONAL | compiler/backends/diffusion_metric.py; existing METRIC-CANDIDATE=CONDITIONAL status (free time parameter t, non-unique) unchanged. |
| d(i,j) -> g_munu (metric) | UNRESOLVED | CL-METRIC-TO-CONNECTION (existing chainlink) remains OPEN; confirmed here as a genuinely self-documented open gap, not a fabricated edge -- see CATEGORY_TRANSLATION_AUDIT.md. |
| g_munu -> nabla -> Riemann -> Ricci -> Einstein tensor | NOT ATTEMPTED THIS PHASE (blocked by the prior arrow's OPEN status: no g_munu construction exists to differentiate) | -- |
| Discrete Cartan identity (This from That 5.1) | PARTIALLY COMPUTED: symmetric term VERIFIED exactly (TFT-002/002B); antisymmetric/curvature term NOT COMPUTABLE FROM AVAILABLE DEFINITIONS (missing: explicit discrete Lie derivative L_e). | simplicial.py |
| D_+ = sqrt(L) locality (Spectral Codex) | FALSIFIED (existing H2, unchanged) | compiler/backends/toe_closure_hypotheses.py |
| Alternative block-incidence Dirac operator D=[[0,d1],[d1^T,0]] locality (H2B, new claim) | COMPUTED: exactly local by construction (sparsity 0.38% vs sqrt(L)'s 100%), self-adjoint=True | dirac_candidates.py |
| Mass spectrum m_n = m_0 sqrt(lambda_n) | COMPUTED, predictive content NOT ESTABLISHED: fixed topologies fail by 1-2 orders of magnitude against real tau/mu; an erdos_renyi seed sweep did not improve this. | mass_spectrum.py |
| Gauge group G2/Spin(8) intersection route | FALSIFIED (existing H4, unchanged, rank obstruction) | compiler/backends/toe_closure_hypotheses.py |
| Gauge group Aut(O)xSpin(8) direct-product route | UNCONSTRUCTED (existing H4) + PARTIALLY EXTENDED here: SU(3) subset G2 is CONDITIONALLY SUPPORTED (real, standard external Lie theory); SU(2)xU(1) subset Spin(8) is UNRESOLVED (rank/dimension necessary conditions satisfied, no explicit embedding constructed) | gauge_rank.py |
| SEIT-7 commutant-algebra (3,2,1)-degeneracy gauge mechanism | NOT COMPUTABLE FROM AVAILABLE DEFINITIONS -- no graph construction rule specified anywhere in the corpus for 'the vacuum state' whose spectrum would need checking | gauge_rank.py (H4C) |
| Mosco/spectral convergence of the DESI sparse N-scaling sequence | COMPUTED (numerical evidence only, not a rigorous M1/M2 proof -- missing identification map H_n -> H): uniform data shows convergence-consistent decay; DESI/clustered real data does NOT, consistent with the existing CONTINUUM-LIMIT-L-DESI=FAIL. | convergence.py |
| Chainlink projection structure-preservation (categorical/translation claim) | COMPUTED: 15/16 chainlinks directly backed by real dependency edges, remainder self-documented as open gaps, 0 genuine violations | categorical.py |
