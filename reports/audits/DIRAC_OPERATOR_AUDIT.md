# DIRAC_OPERATOR_AUDIT.md

## Existing result (unchanged, not re-litigated)

H2-SPECTRAL-TRIPLE-LOCALITY = FAIL for D+=sqrt(L) (compiler/backends/toe_closure_hypotheses.py). Dense: 100% nonzero strict, 23.5% at 0.1%-of-peak threshold, weight extending to graph-distance 50+ on a graph where L itself only connects distance<=3.

## New: exact algebraic identities (sympy, exact arithmetic)

### Test complex: filled_triangle
- **d1 . d2 = 0 (chain complex identity)**: `holds_exactly=True`
- **TFT-002: D=[[0,d1],[d1^T,0]] satisfies D^2 = diag(L0, d1^T d1) exactly (This from That section 5.1, SEIT-6)**: `holds_exactly=True`
- **TFT-002B: the standard (established, external) 3-graded Hodge-Dirac operator D=d+delta satisfies D^2 = diag(L0,L1,L2) exactly on a complex with nonempty 2-cells**: `holds_exactly=True`

### Test complex: tetrahedron_boundary_S2
- **d1 . d2 = 0 (chain complex identity)**: `holds_exactly=True`
- **TFT-002: D=[[0,d1],[d1^T,0]] satisfies D^2 = diag(L0, d1^T d1) exactly (This from That section 5.1, SEIT-6)**: `holds_exactly=True`
- **TFT-002B: the standard (established, external) 3-graded Hodge-Dirac operator D=d+delta satisfies D^2 = diag(L0,L1,L2) exactly on a complex with nonempty 2-cells**: `holds_exactly=True`

### Weitzenbock curvature term (TFT-003)

NOT COMPUTABLE FROM AVAILABLE DEFINITIONS: A concrete combinatorial definition of the discrete Lie derivative operator L_e (as a matrix/operator on cochains) for a specific choice of discrete vector field e on the simplicial complex, satisfying Cartan's formula L_e = d.iota_e + iota_e.d by construction (not merely asserted). This-from-That section 5.1 states the desired adjoint relations (<d a,b> = <a, delta b>, (e^.)^dagger = iota_e) and 'evaluates the inner product sum over arbitrary test cochains' to arrive at the Cartan identity, but never gives L_e, iota_e, or the vector field e as explicit matrices/maps on a concrete complex the way d1 and d2 are given here -- so this half of the claimed derivation cannot be independently re-run; it can only be re-run once a specific discrete vector-field/Lie-derivative construction (several exist in the discrete exterior calculus literature, e.g. Desbrun-Hirani-Leok-Marsden's flat/sharp-operator-based discrete Lie derivative) is chosen and cited as the definition actually being used.

## New: H2B locality test (independent of, does not overwrite, H2)

- D self-adjoint: True
- D^2 = diag(L0, d1^T d1) exactly: True
- sparsity (strict): 0.375% (vs sqrt(L)'s 100%)
- row-0 decay by graph distance: {'0': 1.0, '1': 0.0, '2': 0.0, '3': 0.0, '10': 0.0, '50': 0.0, '100': 0.0}

By construction (built directly from the local incidence matrix d1, never from spectral/functional calculus on L), D is exactly as sparse as d1 itself -- each nonzero entry connects a vertex to an edge it is literally an endpoint of, i.e. locality is exact and structural, not merely 'improved relative to sqrt(L)'. This directly resolves the specific locality failure mode H2 found in D+=sqrt(L) (which was dense: 100% strict, 23.5% at the same 0.1%-of-peak threshold, with weight extending to graph-distance 50+).

### What this does NOT establish

Locality alone does not make D a valid Dirac operator for a Standard-Model-type spectral triple. H2's other findings stand unchanged and apply equally here: the KO-dimension this construction naturally produces has not been shown to be 6 mod 8 (the value the Chamseddine-Connes-Marcolli construction requires), and no algebra representation A, grading, or real structure J compatible with the first-order condition [[D,a],JbJ^-1]=0 has been constructed here or anywhere in the corpus. D2's D^2=diag(L0, d1^T d1) also only recovers the RESTRICTED (2-cell-omitting) Laplacian term, per simplicial.py::check_two_block_dirac_squaring -- see TFT-002 vs TFT-002B.
