"use strict";
// Structured crosswalk data extracted directly from the user-supplied
// canonical documentation (UCG Specification v5, DER Registry v1/v2,
// CMRP Volume IX, UPG Canonical Reference, Unified Rosetta Stone TOE v3,
// Combined Compiler Theories Whitepaper). Every "Doc status" value below
// is transcribed verbatim from the source document named; every
// "Compiler status" value is read from this session's real, executed
// audit of the actual compiler/ codebase and its protocol_matrix.json
// output -- never inferred from the documentation.

const DER_BRANCHES = [
  {
    branch: "SDR — Strict Dependency Relation",
    note: "Definitional axioms governing the dependency partial order itself. Direct compiler analogue: the dependency_audit self-audit (topological-order confirmation) and the duplicate-ID guard in compiler/ir/registry.py enforce the same acyclicity/no-redefinition discipline structurally, without using the DER-SDR numbering.",
    rows: [
      ["DER-SDR-001", "Strict dependency relation, definitional", "CERTIFIED", "Structurally enforced (no DER-ID field)", "Compiler's Registry.add() duplicate-guard + dependency DAG are the working equivalent; never labeled DER-SDR-001."],
      ["DER-SDR-002", "Irreflexivity", "CERTIFIED", "Structurally enforced", "No object ever lists itself as its own dependency; unverified as a standalone check."],
      ["DER-SDR-003", "Transitivity", "CERTIFIED", "Structurally enforced", "Not independently checked as a named theorem."],
      ["DER-SDR-004", "Acyclicity (DAG)", "CERTIFIED", "PASS (dependency_audit)", "Directly verified every real compiler run via topological-order computation over registries.objects/transformations."],
      ["DER-SDR-005", "Recovery admissibility", "CERTIFIED", "Structurally enforced", "Every compiler Object/Transformation declares its own dependencies field; not cross-checked against a DER-numbered predecessor list."],
    ],
  },
  {
    branch: "ORG — Organizational Recovery",
    note: "This is the D-T-C-Π \"organizational grammar\" branch. The compiler's own forward_chain.py registers exactly this chain as a dependency TEMPLATE (spec section 6) -- but explicitly OPEN, not CERTIFIED: \"Dependency template only... not a proof.\" This is the single largest status disagreement in the whole crosswalk: 5 of 10 ORG entries are marked CERTIFIED in the source documentation while the compiler's own registered object for the identical content is OPEN.",
    rows: [
      ["DER-ORG-001", "Grammar G={Δ,τ,κ} is the minimal organizational alphabet", "CERTIFIED", "OPEN (DISTINCTION/TRANSFORMATION-NODE/CONSTRAINT objects)", "Compiler registers the identical D/T/C nodes as an explicit dependency TEMPLATE, OPEN by the compiler's own stated policy, not proved minimal by any executed check."],
      ["DER-ORG-002", "State evolution Ψ_{t+1}=C(T(D(Ψ_t)))", "CERTIFIED", "OPEN (TRANSFORMATION-NODE)", "No compiler code computes an actual Ψ_t sequence anywhere."],
      ["DER-ORG-003", "Persistence fixed point Π=lim Γ^nΨ_0", "CERTIFIED", "OPEN (PERSISTENCE-NODE)", "No fixed-point iteration is executed in the compiler; the persistence sector concept that IS executed (CL-HEATFLOW-TO-KERNEL, the t→∞ heat-kernel projector) is a different, narrower, VERIFIED construction not cross-referenced to DER-ORG-003."],
      ["DER-ORG-004", "Recursive generativity Π⇒Δ'", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "No compiler object represents a persistence state generating a new distinction."],
      ["DER-ORG-005", "Organizational compiler interface", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "No compiler object."],
      ["DER-ORG-006", "Fixed-point equivalence theorem", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent: both source and compiler treat this as unresolved."],
      ["DER-ORG-007", "Organizational Persistence Functional Π_O recovery", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status -- see Π₀ discussion below; a real, partial implementation is newly recommended in §7."],
      ["DER-ORG-008", "Organizational attractor uniqueness", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status."],
      ["DER-ORG-009", "Compiler completeness theorem (= AX-ROG-3)", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status; flagged by CMRP Volume IX as the shared blocking obligation for P vs NP (MPB-004) and Navier-Stokes (MPB-003)."],
      ["DER-ORG-010", "Dependency completeness theorem", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status."],
    ],
  },
  {
    branch: "SPC — Spectral Recovery",
    note: "The branch with the closest genuine alignment between documentation and executed compiler code — the graph → Laplacian → spectrum → heat-kernel chain is exactly what compiler/backends/graph_laplacian.py, spectral.py, and the CL-G-TO-L / CL-L-TO-SPECL / CL-SPECL-TO-HEATFLOW / CL-HEATFLOW-TO-KERNEL chainlinks actually compute.",
    rows: [
      ["DER-SPC-001", "Graph G=(V,E)", "CERTIFIED", "PROPOSED (GRAPH-G-SEED)", "Compiler: directly postulated per spec section 31, honestly PROPOSED rather than derived from a primitive-extraction process."],
      ["DER-SPC-002", "Laplacian L=D-A", "CERTIFIED", "CALCULATED (CL-G-TO-L)", "Elementary linear algebra (symmetric, PSD) — the proof is genuinely trivial; recommend upgrading compiler status to VERIFIED/DERIVED since the proof obligation is essentially free (see §7, quick win)."],
      ["DER-SPC-003", "Spectrum Spec(L)", "CERTIFIED", "VERIFIED (CL-L-TO-SPECL)", "Genuine agreement — real eigendecomposition, cross-checked exactly for n≤8."],
      ["DER-SPC-004", "Heat kernel K_t=e^{-tL}", "CERTIFIED", "VERIFIED (CL-SPECL-TO-HEATFLOW)", "Genuine agreement."],
      ["DER-SPC-005", "Persistence filter R=e^{-βL}", "CERTIFIED", "VERIFIED (CL-HEATFLOW-TO-KERNEL, t→∞ limit)", "Same operator family as K_t; the compiler's kernel-projector result is the β→∞ / t→∞ specialization, not cross-referenced to DER-SPC-005 by name."],
      ["DER-SPC-006", "Spectral fixed point Ω", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status; CMRP Volume IX identifies this as the shared obligation behind the Yang-Mills mass-gap and the general (non-3-manifold) Poincaré fixed-point uniqueness."],
    ],
  },
  {
    branch: "VAR — Variational Recovery",
    note: "Claimed fully CERTIFIED in the source documentation (persistence cost functional, the universal field equation, its Legendre transform, the Einstein–Hilbert action, and the Einstein field equations, with THM-EL/THM-GR-LIMIT giving an explicit worked Euler–Lagrange derivation). The compiler has none of this: MR-017 is an OPEN placeholder object, not a computed functional.",
    rows: [
      ["DER-VAR-001", "Persistence Cost Functional C_Π[y]", "CERTIFIED", "OPEN (VARIATIONAL-NODE)", "No compiler code defines or evaluates C_Π[y] anywhere."],
      ["DER-VAR-002", "Universal Persistence Field Equation (Euler–Lagrange of C_Π)", "CERTIFIED (THM-EL)", "NO_CORRESPONDING_ARTIFACT", "The source gives an explicit closed form (y''_c+Γ^c_{ab}y'_ay'_b=-g^{ca}∇_aI_F); nothing in the compiler evaluates it, symbolically or numerically."],
      ["DER-VAR-003", "Legendre transform", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-VAR-004", "Einstein–Hilbert action S_EH", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "The compiler's Lichnerowicz/Seeley-DeWitt work (VERIFIED) computes heat-kernel coefficients on EXTERNAL control manifolds (flat 2D, round S²/S³) — a genuinely different, narrower, real result, not an S_EH computed from the compiler's own recovered geometry."],
      ["DER-VAR-005", "Einstein field equations (via THM-GR-LIMIT, I_F=0)", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "No compiler code derives the vacuum or matter-coupled Einstein equations from its own primitives."],
    ],
  },
  {
    branch: "GEO — Geometry Recovery",
    note: "Claimed fully CERTIFIED, sourced to \"Belkin-Niyogi 2003\" convergence and \"non-degenerate spectral embedding\" for positive-definiteness of the metric. This is the branch with the sharpest DIRECT CONTRADICTION in the whole crosswalk: the compiler's own independently executed falsification work (FALS-METRIC-UNIQUENESS-*, an eigenvalue-uniqueness counterexample, and the Fisher-Rao rejection, EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION, FALSIFIED) found the diffusion-distance metric candidate to be non-unique and representation-dependent — the opposite of \"CERTIFIED... positive-definite.\"",
    rows: [
      ["DER-GEO-001", "Spectral metric g_{μν} from Spec(L)", "CERTIFIED (PRF-GEO-001)", "CONDITIONAL (CL-DIFFUSION-TO-METRIC)", "DIRECT CONTRADICTION: the compiler's own executed eigenvalue-uniqueness counterexample and Fisher-Rao rejection found this construction non-unique (depends on a free, unjustified diffusion-time parameter t) — the documentation's CERTIFIED claim is not reproduced, and appears actively falsified, by this compiler's own independent numerical work."],
      ["DER-GEO-002", "Levi-Civita connection Γ^c_{ab}", "CERTIFIED", "OPEN (CL-METRIC-TO-CONNECTION)", "Cannot be certified downstream of a metric the compiler itself finds non-unique; the compiler's own OPEN status is the more defensible one given DER-GEO-001's actual status."],
      ["DER-GEO-003", "Riemann tensor R^ρ_{σμν}", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT (independent Ollivier-Ricci route exists instead)", "The compiler's only real curvature result (CL-OPERATOR-TO-CURVATURE-DISCRETE, CALCULATED) is discrete Ollivier-Ricci graph curvature — a genuinely different, weaker object, explicitly NOT a resolution of the Riemann-tensor route."],
      ["DER-GEO-004", "Ricci tensor R_{μν}", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-GEO-005", "Ricci scalar R", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-GEO-006", "Einstein tensor G_{μν} (via contracted Bianchi identity)", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "Note: Combined Compiler Theories Whitepaper Part IV §7.4 independently reports a real, worked graph-spectral derivation of the VACUUM Einstein tensor via constraint-selection (Lovelock-style uniqueness) — genuinely closer to executable than this UCG summary suggests, and worth sourcing directly if this branch is implemented (see §7)."],
    ],
  },
  {
    branch: "GAU — Gauge Recovery",
    note: "Claimed fully CERTIFIED. The compiler has a genuine, though structurally unrelated, point of contact: this session's Connes inner-fluctuation work (OMEGA_B-COUPLED-RECOVERY) computes a real, nonzero \"gauge curvature\" Ω_B''=D_A''²−D_F''² for a finite spectral-triple candidate — arrived at via noncommutative geometry, not via the documentation's graph-Laplacian-native gauge-connection construction. The two are not shown to be the same object.",
    rows: [
      ["DER-GAU-001", "Gauge connection A_μ from L", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "No compiler code recovers a gauge connection from the graph Laplacian directly."],
      ["DER-GAU-002", "Field strength F_{μν}", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-GAU-003", "Covariant derivative D_μ", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-GAU-004", "Yang–Mills equations", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["(cf. GM-005)", "Gauge-curvature-type object", "n/a", "VERIFIED (OMEGA_B-COUPLED-RECOVERY, this session)", "A real, nonzero inner-fluctuation curvature exists in the compiler — via Connes NCG, single generator, finite candidate — not the DER-GAU route and not claimed as equivalent to it."],
    ],
  },
  {
    branch: "QR — Quantum Recovery",
    note: "Claimed fully CERTIFIED for all 8 entries (Hilbert space, Schrödinger equation, Heisenberg equation, uncertainty relation, Clifford algebra, Dirac operator, spin recovery, magnetic moment). The compiler's actual coverage is two narrow, finite, discrete analogues from the finite-spectral-triple work — genuinely real but far short of \"CERTIFIED\" quantum mechanics.",
    rows: [
      ["DER-QR-001", "Hilbert space H from Spec(L)", "CERTIFIED", "PROPOSED (DOUBLED-HILBERT-SPACE-H_F-PRIME)", "Compiler: a FINITE-dimensional Hilbert space for one specific candidate spectral triple, not a general recovery from Spec(L)."],
      ["DER-QR-002", "Schrödinger equation", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "No compiler code derives or evaluates a Schrödinger equation."],
      ["DER-QR-003", "Heisenberg equation", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-QR-004", "Uncertainty relation", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-QR-005", "Clifford algebra", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT (used implicitly, not registered)", "The finite spectral-triple work uses gamma-matrix-like gradings (e.g. γ_F=diag(I,−I)) without registering a general Clifford-algebra recovery object."],
      ["DER-QR-006", "Dirac operator D=√L", "CERTIFIED", "CALCULATED (FINITE-DIRAC-D_B)", "Compiler: a FINITE, discrete, graph-based Dirac-TYPE operator (self-adjoint, grading-anticommuting) for one graph, not the general D=√L construction; the compiler's own H2 investigation separately FALSIFIED D_+=√L's locality, which the documentation's DER-QR-006 does not address."],
      ["DER-QR-007", "Spin recovery", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-QR-008", "Magnetic moment", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
    ],
  },
  {
    branch: "TRC — Thermodynamic Recovery",
    note: "Claimed CERTIFIED for 5 of 6 entries (Π_O, TRC-006, OPEN in the source too). The compiler has a single OPEN placeholder object and nothing computed.",
    rows: [
      ["DER-TRC-001", "Internal energy (first law)", "CERTIFIED", "OPEN (THERMODYNAMICS-NODE)", "—"],
      ["DER-TRC-002", "Entropy S=k_B ln W", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-TRC-003", "Entropy flux J_s=J_q/T", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-TRC-004", "Clausius–Duhem inequality", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-TRC-005", "Fourier heat flux J_q=−κ∇T", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["DER-TRC-006", "Π_O / Π₀ persistence functional", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status — but see §7: δ_spec (the spectral-gap component of Π₀=(δ_spec−λ_c)/σ per the UPG Canonical Reference) is ALREADY computable today from the compiler's own real spectrum data, making this the single most tractable concrete next step in the entire crosswalk."],
    ],
  },
  {
    branch: "CMRC — Conformal Mathematics Recovery Core (string theory, 19 entries)",
    note: "Claimed fully CERTIFIED with a complete worked derivation in the Combined Compiler Theories Whitepaper (embedding field → Nambu-Goto → Polyakov action → Virasoro constraints → central charge → critical dimension D=26, with three explicit certification refinements: bosonic specificity, flat-background assumption, and Einstein equations as a downstream β=0 consequence rather than a direct one). There is no string-theory branch anywhere in the compiler's protocol taxonomy or registries at all — not FAIL, not OPEN, simply absent as a category.",
    rows: [
      ["CMRC-001..019", "Embedding field → Polyakov action → Virasoro algebra → critical dimension D=26 (bosonic)", "CERTIFIED (with 3 stated refinements)", "ABSENT FROM TAXONOMY", "No corresponding layer exists in the compiler's protocol_taxonomy.py at all; recommend adding one only if the user wants full DER-canon coverage (see §7)."],
    ],
  },
  {
    branch: "VAL — MDCL Cross-Domain Validation (5 entries)",
    note: "String theory (=CMRC), Maxwell electrodynamics, GR matter coupling, quantum mechanics (canonical quantization, with the Groenewold–Van Hove obstruction explicitly recorded as a limitation), and Hamiltonian mechanics (symplectic geometry) — all CERTIFIED per the source, with real worked derivations for VAL-001/004/005 and summary-only status for VAL-002/003.",
    rows: [
      ["VAL-001", "Classical & quantum string theory", "CERTIFIED", "ABSENT", "—"],
      ["VAL-002", "Maxwell electrodynamics", "CERTIFIED (summary only)", "ABSENT", "—"],
      ["VAL-003", "GR matter coupling", "CERTIFIED (summary only)", "ABSENT", "—"],
      ["VAL-004", "Quantum mechanics (canonical quantization)", "CERTIFIED", "ABSENT", "Source itself flags the Groenewold–Van Hove obstruction as a real limitation — a good discipline example the compiler should match if this branch is ever implemented."],
      ["VAL-005", "Hamiltonian mechanics (symplectic geometry)", "CERTIFIED", "ABSENT", "—"],
    ],
  },
  {
    branch: "ARBS — Abelian Recursive Bipartite Shell Graph Specification",
    note: "The structural apparatus underlying the entire canon's graph substrate: bipartite vertex partition (Bipartite Reciprocity Lock), shell-nilpotent directed transport (Shell Nilpotency Lock), typed hyperedges, an 8-layer shell index k=0..7, and two terminal certified objects G* (certified graph object) and M* (certified metric object). RF-001..005 (Universal Recovery Functor) and RK-001..003 (Realization Kernel Classification) are CERTIFIED; AU-001/AU-002 (substrate uniqueness) are explicitly OPEN. The compiler's actual registry model (Object/Transformation/Equation, flat, untyped-edge) implements NONE of this structure.",
    rows: [
      ["TH-ARBS-001A", "Bipartite Reciprocity Lock", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "Compiler registries have no bipartite object/operator vertex-type distinction."],
      ["TH-ARBS-001B", "Shell Nilpotency Lock", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "No shell index k exists anywhere in the compiler's Object/Transformation schema."],
      ["RF-001..005", "Universal Recovery Functor (well-definedness, functoriality, 4-topology convergence, monoidal preservation, faithfulness)", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "The compiler's own strong-resolvent/Mosco-convergence discussions (FC-005 continuum-limit work) are a genuine, independent, PARTIALLY-FAILED attempt at a structurally similar convergence claim for one specific case (DESI); not cross-referenced to RF-003."],
      ["RK-001..003", "Realization kernel Lie-groupoid decomposition; gauge symmetries as residual discrete automorphisms", "CERTIFIED", "NO_CORRESPONDING_ARTIFACT", "—"],
      ["AU-001", "Substrate rigidity (unique admissible ARBS category)", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status."],
      ["AU-002", "Singleton preimage collapse (unique G*)", "OPEN (source agrees)", "NO_CORRESPONDING_ARTIFACT", "Consistent open status; CMRP Volume IX flags this as the shared uniqueness obligation behind Yang-Mills, Riemann Hypothesis, and BSD."],
    ],
  },
];

// Headline: the flagship, parameter-free, falsifiable numerical predictions
// stated in UCG Specification v5 §17.4. None have ever been computed by
// the actual compiler code in this repository.
const FLAGSHIP_PREDICTIONS = [
  ["Persistence axion mass", "m_{aP} = 6.885 × 10⁻¹³ eV", "Any confirmed deviation refutes the framework", "Never computed by any compiler module"],
  ["Gravitational-wave background", "f_GW = 166.48 Hz (monochromatic)", "Confirmed flat vacuum at 166.48 Hz refutes the prediction", "Never computed by any compiler module"],
  ["Dwarf spheroidal core radius", "R_c = 120–150 pc (Fornax, Sculptor, Draco)", "Core above 500 pc or below 10 pc falsifies attractor geometry", "Never computed by any compiler module"],
];

// Primitive-grammar reconciliation: the corpus's own PRF-PRIM entry
// (UCG v5 §15) names this "the central open problem across all five
// compiler lines." Transcribed directly.
const PRIMITIVE_GRAMMARS = [
  ["{Δ,τ,κ,Π} — DTC + Persistence", "TOEv Part I §9, MDCL v1.0, DER Registry (PRIM-G-001..004)", "Persistence Π is primitive"],
  ["{Δ,τ,κ} + gradient ∇Φ", "Combined Compiler Theories Whitepaper Part III §2", "Distinction is REPLACED by a directly measurable physical gradient; Persistence is not listed as primitive at all in the 8-stage chain"],
  ["{Δ,τ,κ,Θ,Π,Ω} — MDCL v2.0 extended set", "Combined Compiler Theories Whitepaper Part IV §7.2", "Adds Accessibility (Θ) and Organizational State (Ω) as new primitives beyond DTC+Π"],
  ["{D,T,C} (no Π), Retention derived", "Unified Rosetta Stone TOE v3 §2", "Explicitly proves persistence/Retention is NOT a fourth primitive but a derived fixed-point consequence — directly contradicting the {Δ,τ,κ,Π} set's treatment of Π as primitive"],
];

module.exports = { DER_BRANCHES, FLAGSHIP_PREDICTIONS, PRIMITIVE_GRAMMARS };
