# TFT_BRIDGE_THEOREMS.md

Each This-from-That bridge claim, split into individually-tested propositions per the brief's section IX instruction, rather than treated as one theorem.

## TFT-001: discrete Cartan identity

**STATEMENT (as given in This from That sec.5.1):** L_e = d.iota_e + iota_e.d for a discrete Lie derivative L_e along vector field e, with d, iota_e Hodge-adjoint operators on a simplicial cochain complex.

**STATUS:** NOT COMPUTABLE FROM AVAILABLE DEFINITIONS.

**REQUIRED PROOF / missing object:** A concrete combinatorial definition of the discrete Lie derivative operator L_e (as a matrix/operator on cochains) for a specific choice of discrete vector field e on the simplicial complex, satisfying Cartan's formula L_e = d.iota_e + iota_e.d by construction (not merely asserted). This-from-That section 5.1 states the desired adjoint relations (<d a,b> = <a, delta b>, (e^.)^dagger = iota_e) and 'evaluates the inner product sum over arbitrary test cochains' to arrive at the Cartan identity, but never gives L_e, iota_e, or the vector field e as explicit matrices/maps on a concrete complex the way d1 and d2 are given here -- so this half of the claimed derivation cannot be independently re-run; it can only be re-run once a specific discrete vector-field/Lie-derivative construction (several exist in the discrete exterior calculus literature, e.g. Desbrun-Hirani-Leok-Marsden's flat/sharp-operator-based discrete Lie derivative) is chosen and cited as the definition actually being used.

## TFT-002: two-block Dirac squaring

**STATEMENT:** D=[[0,d1],[d1^T,0]] on C0(+)C1 satisfies D^2=diag(L0,d1^Td1).

**STATUS: VERIFIED EXACT** (sympy, integer/exact arithmetic) on two independent test complexes (a filled triangle and the boundary of a tetrahedron).

**CAVEAT:** this only equals the FULL edge-space Hodge Laplacian L1 when the complex has no 2-cells; see TFT-002B for the complete 3-graded case.

## TFT-002B: full 3-graded Hodge-Dirac squaring (external, established math)

**STATEMENT:** D=d+delta over C0(+)C1(+)C2 satisfies D^2=diag(L0,L1,L2).

**STATUS: VERIFIED EXACT** on the tetrahedron-boundary complex (4 real 2-cells).

## TFT-003: Weitzenbock antisymmetric/curvature term

**STATEMENT:** R_ab = iota_{e_a}L_{e_b} - iota_{e_b}L_{e_a} defines a curvature endomorphism via the discrete Lie derivative of TFT-001.

**STATUS:** NOT COMPUTABLE FROM AVAILABLE DEFINITIONS (depends on TFT-001).

## TFT-004: Wilson lattice gauge action continuum limit

**STATEMENT:** the Wilson plaquette action converges to the continuum Yang-Mills action as lattice spacing -> 0.

**STATUS:** NOT COMPUTABLE FROM AVAILABLE DEFINITIONS.

**Missing object:** a gauge connection U_ij (group-valued edge variable) data structure. No module anywhere in compiler/ or scientific_corpus/ defines a gauge connection on the project's graphs -- only scalar edge weights (plain adjacency) exist. This is external, established physics (Wilson 1974) whose hypotheses this project's own graph construction has not been shown to satisfy, because the required input object does not exist here yet.

## TFT-005: heat-kernel/Fredholm stability -> Atiyah-Singer index structure

**STATUS:** NOT COMPUTABLE FROM AVAILABLE DEFINITIONS.

**Missing object:** same as TFT-004 (no gauge connection) plus a specific elliptic operator with the index-theorem's required ellipticity established for this project's discrete setting -- external, established mathematics (Atiyah-Singer 1963) that this project has not yet connected any of its own constructions to.
