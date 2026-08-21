"""The peer-review protocol taxonomy proposed as "Candidate Universal
Theory Compiler -- Protocol Matrix v1.0" (this session's design
discussion). Pure data: every protocol ID, its layer, its stated
function/target, and the reviewer question it answers -- transcribed
directly from that proposal, not invented here.

This module makes NO claim about whether any protocol is real. It is the
taxonomy side of the crosswalk; compiler/protocol/protocol_matrix.py is
the side that honestly checks, for each ID, whether a real artifact in
THIS repository's canonical registries backs it, and computes status
from that artifact alone -- never from this file.
"""
from __future__ import annotations

from dataclasses import dataclass

LAYER_NAMES: dict[str, str] = {
    "I": "Meta-Compiler / Governance Layer",
    "II": "Primitive-Recovery Layer",
    "III": "Organizational Grammar Layer",
    "IV": "Mathematical Recovery Layer",
    "V": "Statistical / Information-Geometric Layer",
    "VI": "Physical Recovery Layer",
    "VII": "Quantum Recovery Layer",
    "VIII": "Gauge / Representation / Matter Layer",
    "IX": "Spectral / Constants Layer",
    "X": "Cosmological Closure Layer",
    "XI": "Quantum-Gravity / Unification Closure",
    "XII": "Empirical Validation Layer",
    "XIII": "Closure Gate",
}

# Section XIV of the proposal: the layer-level reviewer question and the
# REQUESTED (not achieved) status per layer -- transcribed verbatim from
# the proposal's own table, kept separate from what protocol_matrix.py
# actually computes.
LAYER_REVIEW_QUESTION: dict[str, tuple[str, str]] = {
    "I": ("Is the compiler formally specified?", "Certified"),
    "II": ("Are the primitives genuinely irreducible?", "Certified"),
    "III": ("Does DTC generate the organizational dynamics?", "Certified"),
    "IV": ("Does the mathematical structure follow?", "Certified"),
    "IX": ("Does spectral structure emerge uniquely?", "Certified"),
    "V": ("Does thermodynamics/information geometry emerge?", "Certified"),
    "VI": ("Does GR/classical physics emerge?", "Certified"),
    "VII": ("Does quantum mechanics/QFT emerge?", "Required"),
    "VIII": ("Does the SM structure emerge?", "Required"),
    "X": ("Does cosmology emerge consistently?", "Required"),
    "XI": ("Do all branches close into one theory?", "Required"),
    "XII": ("Does it make discriminating predictions? / Can an independent "
            "group reproduce it?", "Required"),
}


@dataclass(frozen=True)
class ProtocolTaxonomyEntry:
    protocol_id: str
    layer: str
    family_or_target: str
    description: str


TAXONOMY: list[ProtocolTaxonomyEntry] = [
    # I. Meta-Compiler / Governance Layer
    ProtocolTaxonomyEntry("MC-001", "I", "Universal Compiler Specification Protocol",
                          "Defines compiler grammar and execution rules -> canonical compiler specification"),
    ProtocolTaxonomyEntry("MC-002", "I", "Master Dependency ChainLink Protocol (MDCL)",
                          "Establishes the canonical DAG -> dependency graph"),
    ProtocolTaxonomyEntry("MC-003", "I", "Universal Dependency Law Protocol (UDL)",
                          "Determines legal dependency ordering -> partial-order constraints"),
    ProtocolTaxonomyEntry("MC-004", "I", "Universal Registry Protocol",
                          "Registers every symbol, object, operator, equation, theorem -> canonical registries"),
    ProtocolTaxonomyEntry("MC-005", "I", "Provenance Protocol",
                          "Records origin of every result -> provenance chain"),
    ProtocolTaxonomyEntry("MC-006", "I", "Status Admissibility Protocol",
                          "Separates DERIVED/VERIFIED/CALCULATED/PROPOSED/OPEN/REJECTED -> admissibility ledger"),
    ProtocolTaxonomyEntry("MC-007", "I", "Proof Dependency Graph Protocol (PDG)",
                          "Maps every proof obligation -> proof DAG"),
    ProtocolTaxonomyEntry("MC-008", "I", "Canonical Representation Protocol",
                          "Ensures one canonical representation per object -> normal form"),
    ProtocolTaxonomyEntry("MC-009", "I", "Reproducibility Protocol",
                          "Makes every derivation executable/reconstructable -> reproduction specification"),
    ProtocolTaxonomyEntry("MC-010", "I", "Falsification Protocol",
                          "Defines how candidate results can fail -> falsification criteria"),

    # II. Primitive-Recovery Layer
    ProtocolTaxonomyEntry("PR-001", "II", "Primitive Extraction Protocol",
                          "Extract candidate primitives from any domain -> candidate primitive set"),
    ProtocolTaxonomyEntry("PR-002", "II", "Structural Elimination Protocol (SEP)",
                          "Remove nonessential structure recursively -> irreducible structure"),
    ProtocolTaxonomyEntry("PR-003", "II", "Representation Invariance Test (RIT)",
                          "Remove observer/representation artifacts -> representation-invariant structures"),
    ProtocolTaxonomyEntry("PR-004", "II", "Mathematical Invariance Test (MIT)",
                          "Test mathematically equivalent descriptions -> mathematical invariants"),
    ProtocolTaxonomyEntry("PR-005", "II", "Primitive Independence Protocol",
                          "Test whether primitives are mutually reducible -> independent primitive set"),
    ProtocolTaxonomyEntry("PR-006", "II", "Irreducibility Certification Protocol",
                          "Certify that no primitive can be eliminated -> certified primitive basis"),
    ProtocolTaxonomyEntry("PR-007", "II", "Primitive Reconstruction Protocol",
                          "Reconstruct original system from primitives -> reconstruction proof"),
    ProtocolTaxonomyEntry("PR-008", "II", "Domain Compression Protocol",
                          "Compress domain-specific ontology into primitive grammar -> domain-free representation"),

    # III. Organizational Grammar Layer
    ProtocolTaxonomyEntry("OG-001", "III", "Distinction Protocol", "Formalize separability / distinction"),
    ProtocolTaxonomyEntry("OG-002", "III", "Transformation Protocol", "Formalize state transition"),
    ProtocolTaxonomyEntry("OG-003", "III", "Constraint Protocol", "Formalize admissible transformation space"),
    ProtocolTaxonomyEntry("OG-004", "III", "DTC Composition Protocol", "Construct D,T,C compositions"),
    ProtocolTaxonomyEntry("OG-005", "III", "Organizational State Protocol", "Define organizational state Psi"),
    ProtocolTaxonomyEntry("OG-006", "III", "Organizational Dynamics Protocol", "Derive Psi-dot"),
    ProtocolTaxonomyEntry("OG-007", "III", "Organizational Fixed-Point Protocol", "Recover stable organizational states"),
    ProtocolTaxonomyEntry("OG-008", "III", "Persistence Protocol", "Derive persistence sectors"),
    ProtocolTaxonomyEntry("OG-009", "III", "Composition Protocol", "Derive higher-order structures"),
    ProtocolTaxonomyEntry("OG-010", "III", "Hierarchy Protocol", "Derive nested organization"),
    ProtocolTaxonomyEntry("OG-011", "III", "Adaptation Protocol", "Derive response to changing constraints"),
    ProtocolTaxonomyEntry("OG-012", "III", "Evolution Protocol", "Derive organizational state transitions"),

    # IV. Mathematical Recovery Layer
    ProtocolTaxonomyEntry("MR-001", "IV", "State-Space Recovery", "Omega"),
    ProtocolTaxonomyEntry("MR-002", "IV", "Probability/Measure Recovery", "P, mu"),
    ProtocolTaxonomyEntry("MR-003", "IV", "Graph Recovery", "G=(V,E)"),
    ProtocolTaxonomyEntry("MR-004", "IV", "Adjacency Operator Recovery", "A"),
    ProtocolTaxonomyEntry("MR-005", "IV", "Degree Operator Recovery", "D"),
    ProtocolTaxonomyEntry("MR-006", "IV", "Laplacian Recovery", "L = D - A"),
    ProtocolTaxonomyEntry("MR-007", "IV", "Spectral Recovery", "Spec(L)"),
    ProtocolTaxonomyEntry("MR-008", "IV", "Eigenmode Recovery", "(lambda_n, phi_n)"),
    ProtocolTaxonomyEntry("MR-009", "IV", "Persistence-Sector Recovery", "Pi"),
    ProtocolTaxonomyEntry("MR-010", "IV", "Spectral-Distance Recovery", "d(i,j)"),
    ProtocolTaxonomyEntry("MR-011", "IV", "Metric Recovery", "g_munu"),
    ProtocolTaxonomyEntry("MR-012", "IV", "Connection Recovery", "nabla_mu"),
    ProtocolTaxonomyEntry("MR-013", "IV", "Curvature Recovery", "R^rho_sigmamunu"),
    ProtocolTaxonomyEntry("MR-014", "IV", "Ricci Recovery", "R_munu"),
    ProtocolTaxonomyEntry("MR-015", "IV", "Scalar-Curvature Recovery", "R"),
    ProtocolTaxonomyEntry("MR-016", "IV", "Einstein-Tensor Recovery", "G_munu"),
    ProtocolTaxonomyEntry("MR-017", "IV", "Variational Recovery", "S"),
    ProtocolTaxonomyEntry("MR-018", "IV", "Euler-Lagrange Recovery", "Field equations"),

    # V. Statistical / Information-Geometric Layer
    ProtocolTaxonomyEntry("SG-001", "V", "Distribution Recovery", "P(x)"),
    ProtocolTaxonomyEntry("SG-002", "V", "Expectation Recovery", "E[X]"),
    ProtocolTaxonomyEntry("SG-003", "V", "Variance Recovery", "Var(X)"),
    ProtocolTaxonomyEntry("SG-004", "V", "Entropy Recovery", "H(P)"),
    ProtocolTaxonomyEntry("SG-005", "V", "Partition Function Recovery", "Z"),
    ProtocolTaxonomyEntry("SG-006", "V", "Free-Energy Recovery", "F"),
    ProtocolTaxonomyEntry("SG-007", "V", "Generator Recovery", "L (generator)"),
    ProtocolTaxonomyEntry("SG-008", "V", "Spectral Relaxation Protocol", "tau, lambda_gap"),
    ProtocolTaxonomyEntry("SG-009", "V", "Mutual-Information Recovery", "I(X;Y)"),
    ProtocolTaxonomyEntry("SG-010", "V", "KL-Divergence Recovery", "D_KL"),
    ProtocolTaxonomyEntry("SG-011", "V", "Fisher-Information Recovery", "F_ij"),
    ProtocolTaxonomyEntry("SG-012", "V", "Fisher-Rao Metric Recovery", "g_ij^FR"),
    ProtocolTaxonomyEntry("SG-013", "V", "Information Connection Recovery", "Gamma^k_ij"),
    ProtocolTaxonomyEntry("SG-014", "V", "Information Curvature Recovery", "R^k_lij"),
    ProtocolTaxonomyEntry("SG-015", "V", "Statistical-Einstein Recovery", "G_munu^info"),

    # VI. Physical Recovery Layer
    ProtocolTaxonomyEntry("PH-001", "VI", "Conservation Recovery", "Conserved quantities"),
    ProtocolTaxonomyEntry("PH-002", "VI", "Energy-Momentum Recovery", "T_munu"),
    ProtocolTaxonomyEntry("PH-003", "VI", "Continuity Recovery", "nabla^mu T_munu = 0"),
    ProtocolTaxonomyEntry("PH-004", "VI", "Einstein Equation Recovery", "G_munu + Lambda g_munu = alpha T_munu"),
    ProtocolTaxonomyEntry("PH-005", "VI", "Newtonian Limit Protocol", "Newtonian gravity"),
    ProtocolTaxonomyEntry("PH-006", "VI", "Geodesic Recovery", "Free-fall dynamics"),
    ProtocolTaxonomyEntry("PH-007", "VI", "Lorentzian Signature Recovery", "Spacetime causal structure"),
    ProtocolTaxonomyEntry("PH-008", "VI", "Relativistic Field Recovery", "Relativistic dynamics"),
    ProtocolTaxonomyEntry("PH-009", "VI", "Thermodynamic Recovery", "S, T, U, F, ..."),
    ProtocolTaxonomyEntry("PH-010", "VI", "Clausius-Duhem Recovery", "Entropy inequality"),
    ProtocolTaxonomyEntry("PH-011", "VI", "Fourier Recovery", "q^mu = -kappa nabla^mu T"),
    ProtocolTaxonomyEntry("PH-012", "VI", "Hydrodynamic Recovery", "Navier-Stokes"),
    ProtocolTaxonomyEntry("PH-013", "VI", "Electromagnetic Recovery", "Maxwell equations"),

    # VII. Quantum Recovery Layer
    ProtocolTaxonomyEntry("QR-001", "VII", "Phase-Space Recovery", "Classical phase space"),
    ProtocolTaxonomyEntry("QR-002", "VII", "Poisson-Bracket Recovery", "{A,B}"),
    ProtocolTaxonomyEntry("QR-003", "VII", "Quantization Protocol", "{A,B} -> [A,B]"),
    ProtocolTaxonomyEntry("QR-004", "VII", "Hilbert-Space Recovery", "H"),
    ProtocolTaxonomyEntry("QR-005", "VII", "Operator Recovery", "A-hat"),
    ProtocolTaxonomyEntry("QR-006", "VII", "Canonical Commutator Recovery", "[x-hat,p-hat] = i*hbar"),
    ProtocolTaxonomyEntry("QR-007", "VII", "Hamiltonian Recovery", "H-hat"),
    ProtocolTaxonomyEntry("QR-008", "VII", "Schroedinger Recovery", "i*hbar*d_t psi = H-hat psi"),
    ProtocolTaxonomyEntry("QR-009", "VII", "Lagrangian Quantum Recovery", "Quantum action"),
    ProtocolTaxonomyEntry("QR-010", "VII", "Path-Integral Recovery", "Integral D-phi e^(iS/hbar)"),
    ProtocolTaxonomyEntry("QR-011", "VII", "Field Quantization Recovery", "QFT"),
    ProtocolTaxonomyEntry("QR-012", "VII", "Dirac Recovery", "Dirac equation"),
    ProtocolTaxonomyEntry("QR-013", "VII", "Gauge-Field Quantization", "Gauge QFT"),
    ProtocolTaxonomyEntry("QR-014", "VII", "Renormalization Recovery", "RG structure"),

    # VIII. Gauge / Representation / Matter Layer
    ProtocolTaxonomyEntry("GM-001", "VIII", "Symmetry Recovery", "Continuous/discrete symmetries"),
    ProtocolTaxonomyEntry("GM-002", "VIII", "Group Recovery", "Lie-group structure"),
    ProtocolTaxonomyEntry("GM-003", "VIII", "Representation Recovery", "Matter representations"),
    ProtocolTaxonomyEntry("GM-004", "VIII", "Gauge-Connection Recovery", "Gauge fields"),
    ProtocolTaxonomyEntry("GM-005", "VIII", "Gauge-Curvature Recovery", "Field strengths"),
    ProtocolTaxonomyEntry("GM-006", "VIII", "Yang-Mills Recovery", "Yang-Mills equations"),
    ProtocolTaxonomyEntry("GM-007", "VIII", "Standard-Model Gauge Recovery", "SU(3)xSU(2)xU(1)"),
    ProtocolTaxonomyEntry("GM-008", "VIII", "Matter Representation Recovery", "Quarks/leptons"),
    ProtocolTaxonomyEntry("GM-009", "VIII", "Higgs-Sector Recovery", "Higgs structure"),
    ProtocolTaxonomyEntry("GM-010", "VIII", "Mass-Generation Recovery", "Mass spectrum"),
    ProtocolTaxonomyEntry("GM-011", "VIII", "Charge Quantization Protocol", "Charge structure"),
    ProtocolTaxonomyEntry("GM-012", "VIII", "Generation Recovery", "Fermion generations"),
    ProtocolTaxonomyEntry("GM-013", "VIII", "Coupling Recovery", "Gauge couplings"),

    # IX. Spectral / Constants Layer
    ProtocolTaxonomyEntry("SC-001", "IX", "Spectral Observable Protocol", "Observable spectral quantities"),
    ProtocolTaxonomyEntry("SC-002", "IX", "Eigenvalue Interpretation Protocol", "Physical interpretation of lambda_n"),
    ProtocolTaxonomyEntry("SC-003", "IX", "Ground-State Subtraction Protocol", "lambda_n - lambda_0"),
    ProtocolTaxonomyEntry("SC-004", "IX", "Spectral-Gap Protocol", "Delta lambda"),
    ProtocolTaxonomyEntry("SC-005", "IX", "Scale-Recovery Protocol", "Physical units"),
    ProtocolTaxonomyEntry("SC-006", "IX", "Planck-Scale Recovery", "l_P, t_P, E_P, ..."),
    ProtocolTaxonomyEntry("SC-007", "IX", "Mass-Spectrum Protocol", "m_n"),
    ProtocolTaxonomyEntry("SC-008", "IX", "Coupling-Spectrum Protocol", "alpha_k"),
    ProtocolTaxonomyEntry("SC-009", "IX", "Constant-Recovery Protocol", "Dimensionless constants"),
    ProtocolTaxonomyEntry("SC-010", "IX", "Dimensionless-Ratio Protocol", "Observable ratios"),
    ProtocolTaxonomyEntry("SC-011", "IX", "Spectral-to-Physical Map", "lambda -> O_phys"),
    ProtocolTaxonomyEntry("SC-012", "IX", "Uniqueness/Falsification Protocol", "Tests whether mapping is unique"),

    # X. Cosmological Closure Layer
    ProtocolTaxonomyEntry("CO-001", "X", "Cosmological State Recovery", "Initial/fundamental state"),
    ProtocolTaxonomyEntry("CO-002", "X", "Expansion Recovery", "a(t)"),
    ProtocolTaxonomyEntry("CO-003", "X", "Friedmann Recovery", "Friedmann equations"),
    ProtocolTaxonomyEntry("CO-004", "X", "Early-Universe Recovery", "Early cosmological dynamics"),
    ProtocolTaxonomyEntry("CO-005", "X", "Inflation/Alternative Recovery", "Early expansion mechanism"),
    ProtocolTaxonomyEntry("CO-006", "X", "Big-Bang Boundary Protocol", "Initial-limit behavior"),
    ProtocolTaxonomyEntry("CO-007", "X", "CMB Recovery", "CMB observables"),
    ProtocolTaxonomyEntry("CO-008", "X", "Structure-Formation Recovery", "Large-scale structure"),
    ProtocolTaxonomyEntry("CO-009", "X", "Dark-Energy Protocol", "Accelerated expansion"),
    ProtocolTaxonomyEntry("CO-010", "X", "DESI Constraint Protocol", "BAO / DESI observables"),
    ProtocolTaxonomyEntry("CO-011", "X", "Gravitational-Wave Protocol", "GW propagation"),
    ProtocolTaxonomyEntry("CO-012", "X", "Cosmological Parameter Recovery", "Omega_i, H0, ..."),

    # XI. Quantum-Gravity / Unification Closure
    ProtocolTaxonomyEntry("UG-001", "XI", "Gravity-Quantum Compatibility", "Compatibility conditions"),
    ProtocolTaxonomyEntry("UG-002", "XI", "Quantum-Geometry Protocol", "Quantum geometry"),
    ProtocolTaxonomyEntry("UG-003", "XI", "Spectral-Geometry Quantization", "Quantized spectral structure"),
    ProtocolTaxonomyEntry("UG-004", "XI", "Gauge-Geometry Unification", "Common mathematical structure"),
    ProtocolTaxonomyEntry("UG-005", "XI", "Matter-Geometry Coupling", "Unified coupling"),
    ProtocolTaxonomyEntry("UG-006", "XI", "Information-Geometry-Quantum Closure", "Cross-branch consistency"),
    ProtocolTaxonomyEntry("UG-007", "XI", "UV-Consistency Protocol", "High-energy consistency"),
    ProtocolTaxonomyEntry("UG-008", "XI", "Classical-Limit Protocol", "Recovery of classical physics"),
    ProtocolTaxonomyEntry("UG-009", "XI", "Quantum-Limit Protocol", "Recovery of quantum physics"),
    ProtocolTaxonomyEntry("UG-010", "XI", "Unified Action Protocol", "Single candidate action"),
    ProtocolTaxonomyEntry("UG-011", "XI", "Unified Equation Protocol", "Single candidate governing equation"),
    ProtocolTaxonomyEntry("UG-012", "XI", "Unification Closure Test", "Full DAG closure"),

    # XII. Empirical Validation Layer
    ProtocolTaxonomyEntry("EV-001", "XII", "Dimensional Consistency", "Units"),
    ProtocolTaxonomyEntry("EV-002", "XII", "Symmetry Consistency", "Required symmetries"),
    ProtocolTaxonomyEntry("EV-003", "XII", "Conservation Consistency", "Conservation laws"),
    ProtocolTaxonomyEntry("EV-004", "XII", "Classical-Limit Test", "c, hbar -> appropriate limits"),
    ProtocolTaxonomyEntry("EV-005", "XII", "Newtonian-Limit Test", "GR -> Newton"),
    ProtocolTaxonomyEntry("EV-006", "XII", "Quantum-Limit Test", "Classical -> quantum structure"),
    ProtocolTaxonomyEntry("EV-007", "XII", "Standard-Model Test", "Known particle physics"),
    ProtocolTaxonomyEntry("EV-008", "XII", "Cosmology Test", "CMB/BAO/etc."),
    ProtocolTaxonomyEntry("EV-009", "XII", "Gravitational-Wave Test", "GW propagation"),
    ProtocolTaxonomyEntry("EV-010", "XII", "Spectral Prediction Test", "New spectral observables"),
    ProtocolTaxonomyEntry("EV-011", "XII", "Parameter Prediction Test", "No free fitting where derivation forbids it"),
    ProtocolTaxonomyEntry("EV-012", "XII", "Novel-Prediction Test", "At least one discriminating prediction"),
    ProtocolTaxonomyEntry("EV-013", "XII", "Independent-Reproduction Test", "Independent implementation"),
    ProtocolTaxonomyEntry("EV-014", "XII", "Blind-Prediction Test", "Prediction before comparison"),
    ProtocolTaxonomyEntry("EV-015", "XII", "Falsification Closure", "Explicit failure conditions"),

    # XIII. Closure Gate
    ProtocolTaxonomyEntry("UCC-001", "XIII", "Universal Closure Protocol",
                          "T -> R (recovered math) -> P (recovered physics) -> E (predictions); "
                          "T not<= empirical target selection"),
]

TAXONOMY_BY_ID: dict[str, ProtocolTaxonomyEntry] = {e.protocol_id: e for e in TAXONOMY}
