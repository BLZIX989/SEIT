# PEER_REVIEW_STATUS_MATRIX.md

Crosswalk of the "Candidate Universal Theory Compiler -- Protocol Matrix v1.0" taxonomy (a design proposal discussed and agreed for this repository) against this repository's REAL canonical MDCL registries. Every status below is read directly off a real Object, Transformation, Chainlink, self-audit result, registered Protocol, or on-disk document THIS compiler run produced -- see compiler/protocol/protocol_matrix.py's `_CORRESPONDENCES` dict for the exact, explicit, hand-checked mapping. A protocol with no entry there is reported as `NO_CORRESPONDING_ARTIFACT`, not silently omitted and not guessed at.

**Scope**: this crosswalk reads only the registries `python3 -m compiler.run_compiler` itself produces. Real work exists elsewhere in this repository (`scientific_corpus/derivation/`, `seit_lang/`) that is not registered into these canonical registries; where that matters for a specific protocol, the per-protocol note below says so explicitly rather than reaching outside this run's own artifacts.

## Layer summary

| Layer | Name | Reviewer question | Requested status | Protocols | With real backing | No corresponding artifact |
|---|---|---|---|---|---|---|
| I | Meta-Compiler / Governance Layer | Is the compiler formally specified? | Certified | 10 | 9 | 1 |
| II | Primitive-Recovery Layer | Are the primitives genuinely irreducible? | Certified | 8 | 3 | 5 |
| III | Organizational Grammar Layer | Does DTC generate the organizational dynamics? | Certified | 12 | 5 | 7 |
| IV | Mathematical Recovery Layer | Does the mathematical structure follow? | Certified | 18 | 10 | 8 |
| V | Statistical / Information-Geometric Layer | Does thermodynamics/information geometry emerge? | Certified | 15 | 2 | 13 |
| VI | Physical Recovery Layer | Does GR/classical physics emerge? | Certified | 13 | 1 | 12 |
| VII | Quantum Recovery Layer | Does quantum mechanics/QFT emerge? | Required | 14 | 2 | 12 |
| VIII | Gauge / Representation / Matter Layer | Does the SM structure emerge? | Required | 13 | 5 | 8 |
| IX | Spectral / Constants Layer | Does spectral structure emerge uniquely? | Certified | 12 | 2 | 10 |
| X | Cosmological Closure Layer | Does cosmology emerge consistently? | Required | 12 | 2 | 10 |
| XI | Quantum-Gravity / Unification Closure | Do all branches close into one theory? | Required | 12 | 1 | 11 |
| XII | Empirical Validation Layer | Does it make discriminating predictions? / Can an independent group reproduce it? | Required | 15 | 4 | 11 |
| XIII | Closure Gate |  |  | 1 | 0 | 1 |

"With real backing" means the protocol resolved to a real registry artifact -- it does **not** mean that artifact's status is VERIFIED or DERIVED. A protocol counts as backed even when the real artifact's status is FAIL, FALSIFIED, or OPEN: what this column measures is whether the question is answered by something real and checkable, not whether the answer is favorable.

## Full protocol matrix

| Protocol | Layer | Family/Target | Computed status | Evidence |
|---|---|---|---|---|
| MC-001 | I | Universal Compiler Specification Protocol | DOCUMENT_EXISTS | FORWARD_MDCL_COMPILER_SPEC.md: found at repository root |
| MC-002 | I | Master Dependency ChainLink Protocol (MDCL) | DOCUMENT_EXISTS | master_mdcl.json: found at repository root |
| MC-003 | I | Universal Dependency Law Protocol (UDL) | PASS | self_audit dependency_audit: passed=True, 0 issues -- topological-order confirmation over the real dependency DAG |
| MC-004 | I | Universal Registry Protocol | DOCUMENT_EXISTS | object_registry.json: found at repository root -- one of several universal registries this run produced; see also transformation_registry.json, equation_registry.json |
| MC-005 | I | Provenance Protocol | PASS | self_audit provenance_audit: passed=True, 0 issues |
| MC-006 | I | Status Admissibility Protocol | PASS | self_audit status_audit: passed=True, 0 issues |
| MC-007 | I | Proof Dependency Graph Protocol (PDG) | DOCUMENT_EXISTS | chainlink_registry.json: found at repository root -- the Chainlink layer plays the PDG role: dependencies + proof_status per edge, status always computed from a real Transformation/Object |
| MC-008 | I | Canonical Representation Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MC-009 | I | Reproducibility Protocol | PASS | self_audit numerical_reproducibility_audit: passed=True, 0 issues |
| MC-010 | I | Falsification Protocol | REGISTERED | formally registered as PROTOCOL-STRUCTURAL-FALSIFICATION in protocol_registry.json |
| PR-001 | II | Primitive Extraction Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PR-002 | II | Structural Elimination Protocol (SEP) | CODE_EXISTS_AND_CALLABLE | compiler.falsification.protocols:structural_elimination_protocol: importable and callable |
| PR-003 | II | Representation Invariance Test (RIT) | CODE_EXISTS_AND_CALLABLE | compiler.falsification.protocols:representation_invariance_test: importable and callable |
| PR-004 | II | Mathematical Invariance Test (MIT) | CODE_EXISTS_AND_CALLABLE | compiler.falsification.protocols:mathematical_invariance_test: importable and callable |
| PR-005 | II | Primitive Independence Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PR-006 | II | Irreducibility Certification Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PR-007 | II | Primitive Reconstruction Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PR-008 | II | Domain Compression Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| OG-001 | III | Distinction Protocol | OPEN | object DISTINCTION: status=OPEN; carrier='D(Omega_1, Omega_0)' |
| OG-002 | III | Transformation Protocol | OPEN | object TRANSFORMATION-NODE: status=OPEN; carrier='f: Omega_i -> Omega_j' |
| OG-003 | III | Constraint Protocol | OPEN | object CONSTRAINT: status=OPEN; carrier='C = Adm(T)' |
| OG-004 | III | DTC Composition Protocol | OPEN | object RELATION: status=OPEN; carrier='R(Omega_i, Omega_j)' -- R(Omega_i,Omega_j) is the template's composition point between Distinction and Transformation |
| OG-005 | III | Organizational State Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| OG-006 | III | Organizational Dynamics Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| OG-007 | III | Organizational Fixed-Point Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| OG-008 | III | Persistence Protocol | OPEN | object PERSISTENCE-NODE: status=OPEN; carrier='I[Phi_t Omega] = I[Omega]' |
| OG-009 | III | Composition Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| OG-010 | III | Hierarchy Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| OG-011 | III | Adaptation Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| OG-012 | III | Evolution Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-001 | IV | State-Space Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-002 | IV | Probability/Measure Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-003 | IV | Graph Recovery | PROPOSED | object GRAPH-G-SEED: status=PROPOSED; carrier="A graph G=(V,E), directly postulated as a candidate mathematical object per spec section 31's own framing of the first executable test; not claimed to descend f" |
| MR-004 | IV | Adjacency Operator Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-005 | IV | Degree Operator Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-006 | IV | Laplacian Recovery | CALCULATED | chainlink CL-G-TO-L: status=CALCULATED; statement='L = D - A for graph G=(V,E)' |
| MR-007 | IV | Spectral Recovery | VERIFIED | chainlink CL-L-TO-SPECL: status=VERIFIED; statement='L phi_n = lambda_n phi_n' |
| MR-008 | IV | Eigenmode Recovery | VERIFIED | chainlink CL-L-TO-SPECL: status=VERIFIED; statement='L phi_n = lambda_n phi_n' -- eigenmodes (lambda_n,phi_n) are the content of the spectrum computed here |
| MR-009 | IV | Persistence-Sector Recovery | VERIFIED | chainlink CL-HEATFLOW-TO-KERNEL: status=VERIFIED; statement='lim_{t->inf} e^{-tL} = P_ker(L)' -- the t->inf kernel projector IS this system's persistence sector |
| MR-010 | IV | Spectral-Distance Recovery | CALCULATED | chainlink CL-SPECL-TO-DIFFUSION: status=CALCULATED; statement='d_t(i,j)^2 = sum_n e^{-2t lambda_n}(phi_n(i)-phi_n(j))^2' |
| MR-011 | IV | Metric Recovery | CONDITIONAL | chainlink CL-DIFFUSION-TO-METRIC: status=CONDITIONAL; statement='candidate g_ij from diffusion-distance refinement sweep' -- CONDITIONAL: depends on a free, non-unique diffusion-time parameter |
| MR-012 | IV | Connection Recovery | OPEN | chainlink CL-METRIC-TO-CONNECTION: status=OPEN; statement='Gamma^k_ij = 1/2 g^kl (d_i g_jl + d_j g_il - d_l g_ij) (continuum form; no discrete analogue is registered for this candidate)' -- OPEN: the honest frontier -- no admissible connection construction from a non-unique metric candidate is registered |
| MR-013 | IV | Curvature Recovery | CALCULATED | chainlink CL-OPERATOR-TO-CURVATURE-DISCRETE: status=CALCULATED; statement='kappa(x,y) = 1 - W1(m_x,m_y)/d(x,y) (Ollivier-Ricci, alpha=0)' -- Ollivier-Ricci DISCRETE graph curvature -- a real, independent route, NOT the continuum Riemann tensor R^rho_sigmamunu this protocol names; see that chainlink's own note that it does not resolve CL-METRIC-TO-CONNECTION |
| MR-014 | IV | Ricci Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-015 | IV | Scalar-Curvature Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-016 | IV | Einstein-Tensor Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| MR-017 | IV | Variational Recovery | OPEN | object VARIATIONAL-NODE: status=OPEN; carrier='S, delta S = 0, Euler-Lagrange, Hamiltonian' |
| MR-018 | IV | Euler-Lagrange Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-001 | V | Distribution Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-002 | V | Expectation Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-003 | V | Variance Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-004 | V | Entropy Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-005 | V | Partition Function Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-006 | V | Free-Energy Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-007 | V | Generator Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-008 | V | Spectral Relaxation Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-009 | V | Mutual-Information Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-010 | V | KL-Divergence Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-011 | V | Fisher-Information Recovery | PROPOSED | object FISHER-STATISTICAL-FAMILY: status=PROPOSED; carrier='Gaussian N(mu, sigma^2), theta=(mu, sigma)' |
| SG-012 | V | Fisher-Rao Metric Recovery | FALSIFIED | equation EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION: status=FALSIFIED -- FALSIFIED: the Fisher-Rao route was tried and rejected with a counterexample, not silently dropped |
| SG-013 | V | Information Connection Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-014 | V | Information Curvature Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SG-015 | V | Statistical-Einstein Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-001 | VI | Conservation Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-002 | VI | Energy-Momentum Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-003 | VI | Continuity Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-004 | VI | Einstein Equation Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-005 | VI | Newtonian Limit Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-006 | VI | Geodesic Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-007 | VI | Lorentzian Signature Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-008 | VI | Relativistic Field Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-009 | VI | Thermodynamic Recovery | OPEN | object THERMODYNAMICS-NODE: status=OPEN; carrier='U, S, Z, F, entropy production' |
| PH-010 | VI | Clausius-Duhem Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-011 | VI | Fourier Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-012 | VI | Hydrodynamic Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| PH-013 | VI | Electromagnetic Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-001 | VII | Phase-Space Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-002 | VII | Poisson-Bracket Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-003 | VII | Quantization Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-004 | VII | Hilbert-Space Recovery | PROPOSED | object DOUBLED-HILBERT-SPACE-H_F-PRIME: status=PROPOSED; carrier="H_F' = H_F (+) H_F, genuinely complex (C^(2(N0+N1)), not R^(2(N0+N1)) -- J being merely trivial conjugation on a real space was exactly the degeneracy that brok" -- a FINITE-dimensional Hilbert space for a candidate spectral triple, not a general quantum-mechanical Hilbert space |
| QR-005 | VII | Operator Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-006 | VII | Canonical Commutator Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-007 | VII | Hamiltonian Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-008 | VII | Schroedinger Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-009 | VII | Lagrangian Quantum Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-010 | VII | Path-Integral Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-011 | VII | Field Quantization Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-012 | VII | Dirac Recovery | CALCULATED | object FINITE-DIRAC-D_B: status=CALCULATED; carrier="D_F = D_B = [[0,d1],[d1^T,0]], the H2B block-incidence Dirac operator (dirac_candidates.py), chosen as this candidate's D_F because it is local by construction " -- a FINITE, discrete, graph-based Dirac-TYPE operator (self-adjoint, grading-anticommuting), not the continuum Dirac equation for spinor fields on spacetime |
| QR-013 | VII | Gauge-Field Quantization | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| QR-014 | VII | Renormalization Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-001 | VIII | Symmetry Recovery | OPEN | object GAUGE-NODE: status=OPEN; carrier='A_mu, F_munu, gauge algebra (never SU(3)xSU(2)xU(1) as input)' |
| GM-002 | VIII | Group Recovery | OPEN | object H4-DIRECT-PRODUCT-CLAIM-UNCONSTRUCTED: status=OPEN; carrier="The repository's own original claim (Aut(octonions) x Spin(8) superset SU(3)xSU(2)xU(1), a direct product, not an intersection) is NOT ruled out by the H4 rank " -- necessary rank/dimension conditions checked; no explicit embedding constructed |
| GM-003 | VIII | Representation Recovery | OPEN | object MATTER-NODE: status=OPEN; carrier='fermions, representations, chirality, masses' |
| GM-004 | VIII | Gauge-Connection Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-005 | VIII | Gauge-Curvature Recovery | VERIFIED | object OMEGA_B-COUPLED-RECOVERY: status=VERIFIED; carrier="Omega_B'' := D_A''^2 - D_F''^2, D_A''=D_F''+omega+eps'*J''omegaJ''^-1, omega=i*[D_F'',pi'(f)] (single generator). Verified well-posed: D_A'' self-adjoint (True)" -- NCG inner-fluctuation curvature for a finite candidate with ONE generator, not the general non-abelian field-strength tensor F_munu of a continuum gauge theory |
| GM-006 | VIII | Yang-Mills Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-007 | VIII | Standard-Model Gauge Recovery | FALSIFIED | equation EQ-H4-G2-TRIALITY-INTERSECTION-CLAIM: status=FALSIFIED -- FALSIFIED: the G2/Spin(8) triality-intersection route to SU(3)xSU(2)xU(1) specifically, rank obstruction |
| GM-008 | VIII | Matter Representation Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-009 | VIII | Higgs-Sector Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-010 | VIII | Mass-Generation Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-011 | VIII | Charge Quantization Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-012 | VIII | Generation Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| GM-013 | VIII | Coupling Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-001 | IX | Spectral Observable Protocol | VERIFIED | chainlink CL-L-TO-SPECL: status=VERIFIED; statement='L phi_n = lambda_n phi_n' |
| SC-002 | IX | Eigenvalue Interpretation Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-003 | IX | Ground-State Subtraction Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-004 | IX | Spectral-Gap Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-005 | IX | Scale-Recovery Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-006 | IX | Planck-Scale Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-007 | IX | Mass-Spectrum Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-008 | IX | Coupling-Spectrum Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-009 | IX | Constant-Recovery Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-010 | IX | Dimensionless-Ratio Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-011 | IX | Spectral-to-Physical Map | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| SC-012 | IX | Uniqueness/Falsification Protocol | TESTED_SURVIVED | chainlink CL-L-TO-SPECL: falsification_status=TESTED_SURVIVED |
| CO-001 | X | Cosmological State Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-002 | X | Expansion Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-003 | X | Friedmann Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-004 | X | Early-Universe Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-005 | X | Inflation/Alternative Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-006 | X | Big-Bang Boundary Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-007 | X | CMB Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-008 | X | Structure-Formation Recovery | FAIL | chainlink CL-OPERATOR-TO-CONTINUUM-DESI: status=FAIL; statement='L_tilde_(N,eps) = -L_N/(C_K N eps^5), d=3' -- FAIL: DESI graph-Laplacian continuum-limit attempt |
| CO-009 | X | Dark-Energy Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-010 | X | DESI Constraint Protocol | FAIL | object CONTINUUM-LIMIT-L-DESI: status=FAIL; carrier="L_tilde_(N,eps) = -L_N/(C_K N eps^(d+2)), d=3 -> eps^5. CORRECTED from the workbook's eps^(d/2+1)=eps^(5/2), which is only valid under a different (length^2-uni" |
| CO-011 | X | Gravitational-Wave Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| CO-012 | X | Cosmological Parameter Recovery | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-001 | XI | Gravity-Quantum Compatibility | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-002 | XI | Quantum-Geometry Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-003 | XI | Spectral-Geometry Quantization | FAIL | object FINITE-SPECTRAL-TRIPLE-CERTIFICATION: status=FAIL; carrier='Overall certification of (A_F,H_F,D_F,J_F,gamma_F): FAILS. Self-adjointness and grading axioms hold; real-structure signs are degenerate; the first-order condit' -- FAIL for the original candidate; see the coupled-recovery candidate (OMEGA_B-COUPLED-RECOVERY) for the one construction that does pass |
| UG-004 | XI | Gauge-Geometry Unification | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-005 | XI | Matter-Geometry Coupling | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-006 | XI | Information-Geometry-Quantum Closure | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-007 | XI | UV-Consistency Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-008 | XI | Classical-Limit Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-009 | XI | Quantum-Limit Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-010 | XI | Unified Action Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-011 | XI | Unified Equation Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| UG-012 | XI | Unification Closure Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-001 | XII | Dimensional Consistency | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-002 | XII | Symmetry Consistency | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-003 | XII | Conservation Consistency | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-004 | XII | Classical-Limit Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-005 | XII | Newtonian-Limit Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-006 | XII | Quantum-Limit Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-007 | XII | Standard-Model Test | FALSIFIED | equation EQ-H4-G2-TRIALITY-INTERSECTION-CLAIM: status=FALSIFIED |
| EV-008 | XII | Cosmology Test | FAIL | object CONTINUUM-LIMIT-L-DESI: status=FAIL; carrier="L_tilde_(N,eps) = -L_N/(C_K N eps^(d+2)), d=3 -> eps^5. CORRECTED from the workbook's eps^(d/2+1)=eps^(5/2), which is only valid under a different (length^2-uni" |
| EV-009 | XII | Gravitational-Wave Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-010 | XII | Spectral Prediction Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-011 | XII | Parameter Prediction Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-012 | XII | Novel-Prediction Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-013 | XII | Independent-Reproduction Test | PASS | self_audit numerical_reproducibility_audit: passed=True, 0 issues -- INTERNAL bitwise re-run comparison, not independent-group reproduction |
| EV-014 | XII | Blind-Prediction Test | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |
| EV-015 | XII | Falsification Closure | PASS | self_audit leakage_control_audit: passed=True, 0 issues |
| UCC-001 | XIII | Universal Closure Protocol | NO_CORRESPONDING_ARTIFACT | no real artifact in this repository's canonical MDCL registries addresses this protocol |

---
*Generated by compiler/protocol/write_protocol_matrix_report.py from the exact registries this compiler run produced. No status above was asserted from prose.*
