"""
L0 Literature Ingestion — generates the machine-readable deliverables for
Part I (baseline manifest), Part II (backend gap matrix), Part III (literature
extraction registry), Part IV (literature-MDCL crosswalk), Part V
(implementation crosswalk), Part VI (branch recovery map), Part VII (proposed
recovery records), and Part IX (recovery priority matrix) of the L0 literature
ingestion phase.

This script produces ARTIFACTS ONLY. It does not touch object_registry.json,
transformation_registry.json, equation_registry.json, calculation_registry.json,
falsification_registry.json, status_matrix.json, or any other canonical
registry, and does not invoke compiler.run_compiler. Per Part X ("No Automatic
Canonical Promotion"), everything this script writes is external/proposed
material: GAP records, REFERENCE records, CROSSWALK records, PROPOSED RECOVERY
records -- never a DERIVED/VERIFIED/CALCULATED/CLOSED result.
"""
import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIMESTAMP = "2026-08-19T00:00:00Z"


def git_commit_hash() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


# ---------------------------------------------------------------------------
# Part I -- L0_BASELINE_MANIFEST.json
# ---------------------------------------------------------------------------

def build_baseline_manifest() -> dict:
    status_matrix = json.loads((ROOT / "status_matrix.json").read_text())
    status_counts: dict[str, int] = {}
    for node in status_matrix:
        status_counts[node["status"]] = status_counts.get(node["status"], 0) + 1

    return {
        "manifest_type": "L0_BASELINE_MANIFEST",
        "purpose": (
            "Read-only snapshot of canonical theory state taken immediately "
            "before literature ingestion begins (Part I). Nothing in the L0 "
            "phase may alter any value recorded here; if a later artifact "
            "disagrees with this manifest, the manifest is authoritative for "
            "'what the canonical state was at L0 start', not the later artifact."
        ),
        "extraction_timestamp": TIMESTAMP,
        "git_commit": git_commit_hash(),
        "git_branch": "claude/forward-mdcl-compiler-build-ng4k2k",
        "fc005_status": {
            "MATHEMATICAL-CONVERGENCE-DESI": "FAIL / RETRIABLE",
            "CONTINUUM-LIMIT-L-DESI": "FAIL / RETRIABLE",
            "CURVATURE-CLOSURE-DESI": "OPEN",
            "PHYSICAL-VALIDATION-DESI": "OPEN",
            "frozen": True,
            "frozen_reference": "FC005_CHECKPOINT.md",
            "gate_2_entered": False,
            "gate_3_entered": False,
            "note": (
                "Exactly as frozen by FC005_CHECKPOINT.md. This L0 phase does "
                "not rerun, reinterpret, or promote any part of this state."
            ),
        },
        "node_status_counts": status_counts,
        "node_status_total": len(status_matrix),
        "master_validation_campaign_outputs_used_as_input": [
            "MASTER_PHYSICS_VALIDATION_MATRIX.csv",
            "MASTER_PHYSICS_CLOSURE_MATRIX.csv",
            "DEPENDENCY_CLOSURE_AUDIT.csv",
            "DEPENDENCY_CLOSURE_AUDIT.md",
            "INVARIANT_AUDIT.md",
            "SIGN_CONVENTION_REGISTRY.md",
            "CLEAN_ROOM_REPRODUCTION_REPORT.md",
            "MASTER_PHYSICS_VALIDATION_REPORT.md",
        ],
        "branch_inventory": [
            {"branch_id": "Primitive", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "Variational", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "Euler-Lagrange", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "Symmetry", "canonical_status": "NOT REGISTERED", "executable_backend": False},
            {"branch_id": "Conservation", "canonical_status": "NOT REGISTERED", "executable_backend": False},
            {"branch_id": "Geometry", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "GR", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "Statistical", "canonical_status": "VERIFIED (partial -- 1 step)", "executable_backend": True},
            {"branch_id": "Quantum", "canonical_status": "VERIFIED (partial -- 1 step)", "executable_backend": True},
            {"branch_id": "Thermodynamic", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "Spectral", "canonical_status": "VERIFIED (fully closed for its scope)", "executable_backend": True},
            {"branch_id": "DESI", "canonical_status": "FAIL / RETRIABLE (frozen)", "executable_backend": True},
            {"branch_id": "Continuum", "canonical_status": "FAIL / RETRIABLE (frozen)", "executable_backend": True},
            {"branch_id": "Curvature", "canonical_status": "OPEN (code exists, never executed)", "executable_backend": False},
            {"branch_id": "Quantum/Gravity", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "Early-universe/Cosmology", "canonical_status": "OPEN", "executable_backend": False},
            {"branch_id": "Late-universe/Cosmology", "canonical_status": "OPEN (as evolution branch); CALCULATED (as pipeline input only)", "executable_backend": "partial"},
        ],
        "zero_backend_branches": [
            "Primitive", "Variational", "Euler-Lagrange", "Symmetry", "Conservation",
            "Geometry", "GR", "Thermodynamic", "Quantum/Gravity",
            "Early-universe/Cosmology", "Late-universe/Cosmology (as derivation)",
        ],
        "protection_statement": (
            "Literature ingestion in this phase must not alter canonical "
            "registries, equations, dependency edges, status classifications, "
            "MDCL structure, accepted/rejected state, FC-005 state, or "
            "falsification records. Any proposed recovery produced by this "
            "phase exists only as an external/proposed artifact "
            "(L0_PROPOSED_RECOVERY_RECORDS/, CANONICAL_STATUS=PROPOSED) until "
            "independently derived and audited under the existing UOC "
            "validation rules -- a step explicitly NOT taken in this phase."
        ),
    }


# ---------------------------------------------------------------------------
# Part II -- L0_BRANCH_BACKEND_GAP_MATRIX.csv
# ---------------------------------------------------------------------------

GAP_MATRIX_ROWS = [
    dict(BRANCH_ID="Primitive", BRANCH_NAME="Primitive / Selection chain",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=21,
         MISSING_IMPLEMENTATION_TYPE="non-arbitrary Sigma selection functional; entire FOUNDATION..OBSERVABLES-NODE template chain",
         UPSTREAM_DEPENDENCIES="none (root)",
         DOWNSTREAM_DEPENDENCIES="every template-chain branch (Test1/Test2/DESI branches explicitly do NOT descend from this chain)",
         LITERATURE_SUPPORT_AVAILABLE="NO", RECOVERY_PRIORITY="OUT OF SCOPE",
         RECOVERY_STATUS="NOT PURSUED -- would require inventing new physics/ontology, explicitly prohibited"),
    dict(BRANCH_ID="Variational", BRANCH_NAME="Variational structure (S[phi], delta S=0)",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="action functional construction; variational-derivative operator",
         UPSTREAM_DEPENDENCIES="SPECTRUM-NODE (OPEN, blocked on Primitive chain)",
         DOWNSTREAM_DEPENDENCIES="Euler-Lagrange, Symmetry, Conservation, Quantum, Gauge, Matter, Thermodynamic, Cosmology, Observables",
         LITERATURE_SUPPORT_AVAILABLE="PARTIAL", RECOVERY_PRIORITY="1 (highest downstream impact)",
         RECOVERY_STATUS="RECOVERY-CANDIDATE-AVAILABLE -- standard classical field theory variational principle is established external mathematics; connecting it to SPECTRUM-NODE is not addressed by the supplied corpus"),
    dict(BRANCH_ID="Euler-Lagrange", BRANCH_NAME="Euler-Lagrange equations",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="not separately registered; subsumed under VARIATIONAL-NODE",
         UPSTREAM_DEPENDENCIES="VARIATIONAL-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="none registered separately",
         LITERATURE_SUPPORT_AVAILABLE="PARTIAL (standard textbook result, assumed not derived in delivered pages)",
         RECOVERY_PRIORITY="tied to Variational",
         RECOVERY_STATUS="BLOCKED-ON-UPSTREAM"),
    dict(BRANCH_ID="Symmetry", BRANCH_NAME="Noether symmetry -> conserved current",
         CURRENT_CANONICAL_STATUS="NOT REGISTERED", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="no NOETHER-SYMMETRY IR node registered at all",
         UPSTREAM_DEPENDENCIES="VARIATIONAL-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="Conservation",
         LITERATURE_SUPPORT_AVAILABLE="PARTIAL/ANALOGOUS -- Tong Ch.1 rigorously covers Lorentz/Poincare continuous-symmetry group structure; Noether's theorem itself (symmetry -> current) is standard but was not observed in the delivered pages (through section 1.4.4 CPT only)",
         RECOVERY_PRIORITY="3", RECOVERY_STATUS="RECOVERY-CANDIDATE-AVAILABLE (needs VARIATIONAL-NODE closed first)"),
    dict(BRANCH_ID="Conservation", BRANCH_NAME="d_mu J^mu = 0",
         CURRENT_CANONICAL_STATUS="NOT REGISTERED", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="no CONSERVATION-LAW IR node registered at all",
         UPSTREAM_DEPENDENCIES="NOETHER-SYMMETRY (not registered)",
         DOWNSTREAM_DEPENDENCIES="none registered",
         LITERATURE_SUPPORT_AVAILABLE="PARTIAL (standard consequence, not directly shown in delivered pages)",
         RECOVERY_PRIORITY="5", RECOVERY_STATUS="BLOCKED-ON-UPSTREAM"),
    dict(BRANCH_ID="Geometry", BRANCH_NAME="g_munu -> Riemann -> Ricci -> R",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="metric, connection, Riemann/Ricci/scalar curvature computation",
         UPSTREAM_DEPENDENCIES="SPECTRUM-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="GR, Quantum/Gravity Interface",
         LITERATURE_SUPPORT_AVAILABLE="NO -- none of the 3 supplied documents cover differential geometry / GR machinery",
         RECOVERY_PRIORITY="2", RECOVERY_STATUS="NO-LITERATURE-SUPPORT-IN-THIS-CORPUS"),
    dict(BRANCH_ID="GR", BRANCH_NAME="Einstein field equations",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="not separately registered as an IR node; only SEMICLASSICAL-EINSTEIN-EQUATION exists (PROPOSED)",
         UPSTREAM_DEPENDENCIES="GEOMETRY-NODE (OPEN), MATTER-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="Quantum/Gravity Interface",
         LITERATURE_SUPPORT_AVAILABLE="NO", RECOVERY_PRIORITY="7",
         RECOVERY_STATUS="BLOCKED-ON-UPSTREAM / NO-LITERATURE-SUPPORT"),
    dict(BRANCH_ID="Statistical", BRANCH_NAME="Fisher-Rao statistical recovery core",
         CURRENT_CANONICAL_STATUS="VERIFIED (1 step only)", EXECUTABLE_BACKEND_PRESENT="PARTIAL",
         EXECUTABLE_NODE_COUNT=1, MISSING_NODE_COUNT=9,
         MISSING_IMPLEMENTATION_TYPE="broader SRC chain: mu, P, X, E[X], Var(X), H(P), Z, P(x,t), spectral decomposition",
         UPSTREAM_DEPENDENCIES="none for the closed step",
         DOWNSTREAM_DEPENDENCIES="none currently registered",
         LITERATURE_SUPPORT_AVAILABLE="NO -- none of the 3 documents address information geometry / the Fisher-Rao SRC chain",
         RECOVERY_PRIORITY="LOW (1 step already closed; remainder out of campaign scope)",
         RECOVERY_STATUS="PARTIAL-CLOSURE-ACHIEVED, remainder NOT PURSUED"),
    dict(BRANCH_ID="Quantum", BRANCH_NAME="Quantum recovery core",
         CURRENT_CANONICAL_STATUS="VERIFIED (1 guardrail step only)", EXECUTABLE_BACKEND_PRESENT="PARTIAL",
         EXECUTABLE_NODE_COUNT=1, MISSING_NODE_COUNT="unspecified (QUANTUM-NODE full chain: Hilbert space, observables, quantization map)",
         MISSING_IMPLEMENTATION_TYPE="Hilbert-space construction; quantization map from SPECTRUM-NODE",
         UPSTREAM_DEPENDENCIES="VARIATIONAL-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="Gauge, Matter, Thermodynamic, Cosmology, Observables",
         LITERATURE_SUPPORT_AVAILABLE="ANALOGOUS -- Tong Ch.1 gives Weyl/Dirac spinor representations relevant to relativistic-QM structure, but does not supply a quantization map",
         RECOVERY_PRIORITY="4", RECOVERY_STATUS="RECOVERY-CANDIDATE-PARTIAL (blocked on Variational closing first)"),
    dict(BRANCH_ID="Thermodynamic", BRANCH_NAME="Thermodynamic recovery core",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="internal energy, Clausius-Duhem, entropy current, heat flux computation",
         UPSTREAM_DEPENDENCIES="MATTER-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="Cosmology, Observables",
         LITERATURE_SUPPORT_AVAILABLE="NO -- none of the 3 documents address thermodynamics",
         RECOVERY_PRIORITY="9", RECOVERY_STATUS="NO-LITERATURE-SUPPORT"),
    dict(BRANCH_ID="Spectral", BRANCH_NAME="Graph Laplacian / heat-kernel pipeline",
         CURRENT_CANONICAL_STATUS="VERIFIED (fully closed for its scope)", EXECUTABLE_BACKEND_PRESENT="YES",
         EXECUTABLE_NODE_COUNT=15, MISSING_NODE_COUNT=0,
         MISSING_IMPLEMENTATION_TYPE="none", UPSTREAM_DEPENDENCIES="n/a (closed)",
         DOWNSTREAM_DEPENDENCIES="none pursued further", LITERATURE_SUPPORT_AVAILABLE="n/a (already complete)",
         RECOVERY_PRIORITY="N/A", RECOVERY_STATUS="COMPLETE"),
    dict(BRANCH_ID="DESI", BRANCH_NAME="DESI Gate 1 pipeline",
         CURRENT_CANONICAL_STATUS="FAIL / RETRIABLE (frozen)", EXECUTABLE_BACKEND_PRESENT="YES (partial, frozen)",
         EXECUTABLE_NODE_COUNT=3, MISSING_NODE_COUNT="n/a -- frozen, not a recovery target this phase",
         MISSING_IMPLEMENTATION_TYPE="n/a", UPSTREAM_DEPENDENCIES="none (DESI-CATALOGUE is a directly acquired root)",
         DOWNSTREAM_DEPENDENCIES="Continuum, Curvature, Physical-Validation (all blocked)",
         LITERATURE_SUPPORT_AVAILABLE="NO -- none of the 3 documents address graph-Laplacian continuum limits",
         RECOVERY_PRIORITY="FROZEN", RECOVERY_STATUS="FROZEN-DO-NOT-PURSUE per explicit execution override"),
    dict(BRANCH_ID="Continuum", BRANCH_NAME="Discrete -> continuum limit",
         CURRENT_CANONICAL_STATUS="FAIL / RETRIABLE (frozen)", EXECUTABLE_BACKEND_PRESENT="YES (partial, frozen)",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT="n/a -- frozen",
         MISSING_IMPLEMENTATION_TYPE="n/a", UPSTREAM_DEPENDENCIES="OPERATOR-L-DESI (CALCULATED)",
         DOWNSTREAM_DEPENDENCIES="Curvature, Physical-Validation",
         LITERATURE_SUPPORT_AVAILABLE="NO", RECOVERY_PRIORITY="FROZEN",
         RECOVERY_STATUS="FROZEN-DO-NOT-PURSUE per explicit execution override"),
    dict(BRANCH_ID="Curvature", BRANCH_NAME="Curvature closure (heat-kernel coefficients -> kappa)",
         CURRENT_CANONICAL_STATUS="OPEN (code exists, never executed on real data)",
         EXECUTABLE_BACKEND_PRESENT="PRESENT-BUT-UNEXECUTED", EXECUTABLE_NODE_COUNT=0,
         MISSING_NODE_COUNT="n/a -- execution itself is the gap, blocked on Continuum FAIL",
         MISSING_IMPLEMENTATION_TYPE="n/a (Gate 2 never entered, by instruction)",
         UPSTREAM_DEPENDENCIES="MATHEMATICAL-CONVERGENCE-DESI (FAIL)",
         DOWNSTREAM_DEPENDENCIES="Physical-Validation", LITERATURE_SUPPORT_AVAILABLE="NO",
         RECOVERY_PRIORITY="BLOCKED", RECOVERY_STATUS="BLOCKED-ON-UPSTREAM (Gate 1)"),
    dict(BRANCH_ID="Quantum/Gravity", BRANCH_NAME="Quantum-Gravity interface",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="admissible bridge equation between Quantum and GR chains",
         UPSTREAM_DEPENDENCIES="QUANTUM-NODE (OPEN), GEOMETRY-NODE (OPEN), T2-NCG-BRIDGE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="none", LITERATURE_SUPPORT_AVAILABLE="NO -- none of the 3 documents bridge QM/GR",
         RECOVERY_PRIORITY="10", RECOVERY_STATUS="BLOCKED-ON-UPSTREAM (x2)"),
    dict(BRANCH_ID="Early-universe/Cosmology", BRANCH_NAME="Friedmann equations / early-universe evolution",
         CURRENT_CANONICAL_STATUS="OPEN", EXECUTABLE_BACKEND_PRESENT="NO",
         EXECUTABLE_NODE_COUNT=0, MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="early-universe evolution equation of any kind",
         UPSTREAM_DEPENDENCIES="COSMOLOGY-NODE (OPEN), THERMODYNAMICS-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="Observables",
         LITERATURE_SUPPORT_AVAILABLE="PARTIAL/ANALOGOUS -- Ellis/Gaillard/Nanopoulos touch vacuum-stability and inflation implications in their 'open questions' section, topically adjacent but not structurally supplying Friedmann equations",
         RECOVERY_PRIORITY="11", RECOVERY_STATUS="NO-DIRECT-LITERATURE-SUPPORT"),
    dict(BRANCH_ID="Late-universe/Cosmology", BRANCH_NAME="Late-universe evolution / dark-energy EOS",
         CURRENT_CANONICAL_STATUS="OPEN (as evolution branch); CALCULATED (as pipeline input only)",
         EXECUTABLE_BACKEND_PRESENT="PRESENT-AS-INPUT-ONLY", EXECUTABLE_NODE_COUNT=1,
         MISSING_NODE_COUNT=1,
         MISSING_IMPLEMENTATION_TYPE="Friedmann-equation derivation; dark-energy equation-of-state derivation (currently only DESI's own published fiducial parameters are consumed as pipeline input)",
         UPSTREAM_DEPENDENCIES="COSMOLOGY-NODE (OPEN)",
         DOWNSTREAM_DEPENDENCIES="Observables",
         LITERATURE_SUPPORT_AVAILABLE="NO -- none of the 3 documents derive late-universe evolution equations",
         RECOVERY_PRIORITY="12", RECOVERY_STATUS="NO-LITERATURE-SUPPORT"),
]


# ---------------------------------------------------------------------------
# Part III -- LITERATURE_EXTRACTION_REGISTRY.json
# ---------------------------------------------------------------------------

def build_extraction_registry() -> list[dict]:
    items = []

    def add(item_id, source_id, source_title, author, edition, page, section,
             subsection, eq_no, table_no, fig_no, topic, objects, operators,
             equations, derivation, limiting, assumptions, conventions,
             interpretation, experimental, open_problems, metadata):
        items.append({
            "LITERATURE_ITEM_ID": item_id,
            "SOURCE_ID": source_id,
            "SOURCE_TITLE": source_title,
            "AUTHOR": author,
            "EDITION_OR_VERSION": edition,
            "PAGE": page,
            "SECTION": section,
            "SUBSECTION": subsection,
            "EQUATION_NUMBER": eq_no,
            "TABLE_NUMBER": table_no,
            "FIGURE_NUMBER": fig_no,
            "EXACT_TOPIC": topic,
            "MATHEMATICAL_OBJECTS": objects,
            "OPERATORS": operators,
            "EQUATIONS": equations,
            "DERIVATION_DESCRIPTION": derivation,
            "LIMITING_CASES": limiting,
            "ASSUMPTIONS": assumptions,
            "CONVENTIONS": conventions,
            "PHYSICAL_INTERPRETATION": interpretation,
            "EXPERIMENTAL_VALIDATION": experimental,
            "OPEN_PROBLEMS": open_problems,
            "REFERENCE_METADATA": metadata,
            "EXTRACTION_TIMESTAMP": TIMESTAMP,
        })

    tong_meta = {
        "source_type": "graduate lecture notes",
        "institution": "University of Cambridge, Part III Mathematical Tripos",
        "source_hash_if_available": "not computed -- file supplied as chat attachment, no persistent content hash recorded",
        "extraction_coverage": "Introduction + full Chapter 1 'Symmetries', through section 1.4.4 (CPT), page 47. Chapters 2-7 (Higgs mechanism, strong force, anomalies, electroweak, flavour, neutrinos) are visible in the table of contents but were NOT included in the delivered attachment and are NOT extracted from.",
        "source_vetting": "ACCEPTED -- author is an established Cambridge theoretical physicist; content is standard, widely-taught graduate QFT/particle-physics material; no red flags of the kind found in the Hashimoto document.",
    }
    ellis_meta = {
        "source_type": "book chapter, peer-reviewed compilation",
        "publication": "The Standard Theory of Particle Physics, Chapter 14, World Scientific, 2016",
        "license": "Open Access, CC BY-NC 4.0",
        "source_hash_if_available": "not computed -- file supplied as chat attachment, no persistent content hash recorded",
        "extraction_coverage": "Full chapter (20 pages, pp. 255-274 of the source book, references included).",
        "source_vetting": "ACCEPTED -- published by a mainstream academic press, authored by established particle theorists (two of whom, Ellis and Nanopoulos, are highly cited in the SSB/Higgs literature); content is a standard historical/phenomenological review, internally consistent with mainstream Standard Model physics.",
    }
    hashimoto_meta = {
        "source_type": "journal article",
        "publication": "Journal of Innovations in Energy Science (ScholArena)",
        "source_hash_if_available": "not computed -- file supplied as chat attachment, no persistent content hash recorded",
        "extraction_coverage": "Full document read (all pages, references included).",
        "source_vetting": (
            "REJECTED -- disqualified from use as 'established external mathematics' per this "
            "campaign's own Part I.3 prohibition. Specific findings: (1) invented, non-standard "
            "units ('Gp'/Galapagos, 'Skr'/Sakura) with no traceable definition to SI or any "
            "recognized unit system; (2) a self-named free parameter ('the Junichi Parameter', "
            "J) whose value is NOT derived but chosen after the fact, together with an integer "
            "n and an ad hoc constraint x+y=13, specifically so that the computed mass/volume/"
            "ionization-energy for each of 9 test objects (hydrogen atom, electron, Japanese "
            "kilogram prototype, bowling ball, Earth, Moon, Sun, Venus, Jupiter) matches the "
            "already-known measured value; (3) rejection of finite light speed, gauge-boson "
            "exchange, and Newtonian gravitation via informal 'relational physics'/'clockwork "
            "organism' reasoning, without a rigorous derivation replacing them. Finding (2) is "
            "the exact 'fit the desired physical result and then declare it recovered; promote "
            "a numerical coincidence to a derivation' practice this campaign's Master Physics "
            "Validation Campaign Part I.3 explicitly prohibits. This document is retained in the "
            "extraction registry (the instruction was to read ALL supplied PDFs) but every "
            "record from it is marked SOURCE_VETTING=REJECTED and excluded from Parts IV-IX "
            "(no crosswalk, no recovery map entry, no proposed recovery record may cite it)."
        ),
    }

    # --- Tong, "The Standard Model" ---
    add("LIT-001", "LIT-TONG-SM", "The Standard Model (Part III Mathematical Tripos lecture notes)",
        "David Tong", "Cambridge, current online edition", "3-8", "Introduction", None,
        None, None, None,
        "Overview of the Standard Model as a chiral gauge theory; scope of the notes",
        "Standard Model Lagrangian (referenced, not derived in the introduction)",
        "SU(3)xSU(2)xU(1) gauge group; matter content organized into generations",
        None, None,
        "coupling constants g, g', g_s referenced qualitatively", None,
        "Framing statement: the Standard Model is 'the most successful physical theory ever constructed'",
        "qualitative reference to LHC-era experimental success", None, None, tong_meta)
    add("LIT-002", "LIT-TONG-SM", "The Standard Model", "David Tong",
        "Cambridge, current online edition", "9-15", "Chapter 1", "1.1 The Poincare Group",
        None, None, None,
        "Definition and structure of the Lorentz group and Poincare group as the spacetime symmetry group of relativistic field theory",
        "Lorentz transformations Lambda; Poincare group elements (Lambda, a); generators M^{mu nu}, P^mu",
        "SO(3,1) (or its double cover); semidirect product structure R^{1,3} x SO(3,1)",
        "Lie algebra commutation relations for [M,M], [M,P], [P,P]",
        "non-relativistic limit recovers Galilean group (referenced)",
        "flat Minkowski spacetime; mostly-plus or mostly-minus metric signature choice made explicit in the notes (signature convention stated by the source, not independently re-derived here)",
        "signature convention as adopted by the source text (see SIGN_CONVENTION_REGISTRY.md for this project's own, independent convention register)",
        "Spacetime symmetry as the group of transformations preserving the interval ds^2",
        None, None, None, tong_meta)
    add("LIT-003", "LIT-TONG-SM", "The Standard Model", "David Tong",
        "Cambridge, current online edition", "16-28", "Chapter 1", "1.2-1.3 Representations; Weyl and Dirac spinors",
        None, None, None,
        "Classification of Lorentz-group representations; construction of left- and right-handed Weyl spinors and their combination into Dirac spinors",
        "Weyl spinor psi_L, psi_R (2-component); Dirac spinor Psi (4-component); gamma matrices",
        "Lorentz generators in the spinor representation; Dirac operator i*gamma^mu*partial_mu - m",
        "Dirac equation (i gamma^mu partial_mu - m) Psi = 0",
        "massless limit recovers decoupled Weyl equations for psi_L, psi_R separately",
        "4-dimensional Minkowski spacetime; a specific gamma-matrix (Clifford algebra) representation chosen by the source",
        "gamma-matrix convention as adopted by the source text",
        "Spinors as the representation carrying spin-1/2 matter fields (electrons, quarks, neutrinos)",
        None, None, None, tong_meta)
    add("LIT-004", "LIT-TONG-SM", "The Standard Model", "David Tong",
        "Cambridge, current online edition", "29-38", "Chapter 1", "1.4.1-1.4.3 Discrete symmetries C, P, T",
        None, None, None,
        "Definition and action of the discrete symmetries charge conjugation (C), parity (P), and time reversal (T) on fields",
        "Charge-conjugate field Psi^c; parity-transformed field; time-reversed field (antiunitary)",
        "C, P, T operators acting on spinor/vector fields",
        None,
        "Weak interaction explicitly violates P and C individually (referenced, standard result)",
        "T implemented as an antiunitary operator (standard QFT convention)",
        "standard QFT discrete-symmetry conventions as adopted by the source",
        "P: spatial inversion; C: particle<->antiparticle exchange; T: reversal of time's arrow",
        "P violation in weak decays (referenced, historically well-established)", None, None, tong_meta)
    add("LIT-005", "LIT-TONG-SM", "The Standard Model", "David Tong",
        "Cambridge, current online edition", "39-47", "Chapter 1", "1.4.4 CPT",
        None, None, None,
        "Statement of the CPT theorem: the combined operation CPT is an exact symmetry of any local, Lorentz-invariant, unitary QFT",
        "Combined operator CPT", "CPT operator acting jointly on fields",
        None, None,
        "Locality, Lorentz invariance, unitarity of the underlying QFT (the theorem's own stated hypotheses)",
        "standard QFT convention", "CPT invariance as a structural theorem, not an empirical accident",
        "no CPT violation observed experimentally to date (referenced, standard)", None, None, tong_meta)
    add("LIT-006", "LIT-TONG-SM", "The Standard Model", "David Tong",
        "Cambridge, current online edition", "table of contents (pp. i-vi)", "Table of Contents", None,
        None, None, None,
        "Document structure only -- chapter titles for Ch.2 (Broken Symmetries/Higgs Mechanism), Ch.3 (The Strong Force), Ch.4 (Anomalies), Ch.5 (Electroweak Interactions), Ch.6 (Flavour), Ch.7 (Neutrinos)",
        None, None, None, None, None, None, None, None,
        "explicitly NOT extracted -- chapter content itself was not included in the delivered attachment; this record exists only to document that these chapters are known to exist and were not available for extraction, per Part XI's provenance-honesty requirement",
        None, tong_meta)

    # --- Ellis, Gaillard, Nanopoulos, "A Historical Profile of the Higgs Boson" ---
    add("LIT-007", "LIT-EGN-HIGGS", "A Historical Profile of the Higgs Boson (Ch.14 of The Standard Theory of Particle Physics)",
        "John Ellis, Mary K. Gaillard, Dimitri V. Nanopoulos", "World Scientific, 2016", "255-257",
        "14.1", "Introduction / pre-1964 context", None, None, None,
        "Historical context of spontaneous symmetry breaking (SSB) before the 1964 Higgs papers",
        "scalar field phi; symmetry-breaking potential V(phi)", "potential V(phi) with degenerate minima",
        "Goldstone-type potential referenced (not re-derived in this chapter)",
        None, "SSB as a mechanism for generating mass while preserving Lagrangian symmetry",
        "standard SSB convention", "Massless Goldstone bosons arise from SSB of a global continuous symmetry",
        None, "the 'Goldstone theorem obstruction' -- massless Goldstone bosons are not observed for gauge symmetries, motivating the 1964 papers", None, ellis_meta)
    add("LIT-008", "LIT-EGN-HIGGS", "A Historical Profile of the Higgs Boson", "Ellis, Gaillard, Nanopoulos",
        "World Scientific, 2016", "257-260", "14.2", "The 1964 papers (Englert-Brout, Higgs, Guralnik-Hagen-Kibble)",
        None, None, None,
        "The Higgs mechanism: SSB of a LOCAL (gauge) symmetry, converting a would-be Goldstone boson into the longitudinal mode of a massive gauge boson",
        "Higgs field phi (complex scalar doublet); gauge field A_mu; gauge boson mass term",
        "Covariant derivative D_mu = partial_mu - ig A_mu; mass term from |D_mu phi|^2",
        "Gauge-boson mass generation via |D_mu phi|^2 -> m_A^2 A_mu A^mu after SSB (referenced, standard, not re-derived line-by-line in this historical chapter)",
        None,
        "Abelian (U(1)) toy model used for pedagogical presentation in the original papers, later extended to non-Abelian gauge groups",
        "standard gauge-theory convention",
        "Gauge bosons acquire mass without breaking gauge invariance of the Lagrangian itself",
        None, None, None, ellis_meta)
    add("LIT-009", "LIT-EGN-HIGGS", "A Historical Profile of the Higgs Boson", "Ellis, Gaillard, Nanopoulos",
        "World Scientific, 2016", "260-263", "14.3", "Electroweak unification (Glashow-Weinberg-Salam)",
        None, None, None,
        "Application of the Higgs mechanism to SU(2)xU(1) electroweak theory; W and Z boson mass generation; photon remains massless",
        "SU(2)xU(1) gauge fields W^a_mu, B_mu; Higgs doublet phi; physical W^+-, Z, gamma bosons",
        "electroweak covariant derivative; Weinberg angle theta_W mixing",
        "m_W = (1/2) g v; m_Z = m_W / cos(theta_W) (referenced, standard electroweak mass relations)",
        "theta_W -> 0 or coupling limits referenced qualitatively, not derived numerically in this chapter",
        "SU(2)xU(1) gauge structure; single Higgs doublet (minimal Standard Model)",
        "standard electroweak convention",
        "Unified description of electromagnetism and the weak force via SSB",
        "W, Z boson discovery at CERN SppS (1983, referenced historically)", None, None, ellis_meta)
    add("LIT-010", "LIT-EGN-HIGGS", "A Historical Profile of the Higgs Boson", "Ellis, Gaillard, Nanopoulos",
        "World Scientific, 2016", "263-268", "14.4-14.5", "Search history and 2012 discovery",
        None, None, None,
        "Experimental search history (LEP exclusion limits, Tevatron, LHC) culminating in the July 2012 ATLAS/CMS discovery announcement",
        None, None, None, None,
        "search results reported at successive LHC center-of-mass energies (7, 8 TeV)",
        None, "Discovery of a scalar boson consistent with the Standard Model Higgs",
        "measured mass m_H = 125.09 +/- 0.24 GeV (post-discovery combined ATLAS+CMS value, as reported in this chapter)",
        None, None, ellis_meta)
    add("LIT-011", "LIT-EGN-HIGGS", "A Historical Profile of the Higgs Boson", "Ellis, Gaillard, Nanopoulos",
        "World Scientific, 2016", "268-271", "14.6", "Property verification and vacuum stability",
        None, None, None,
        "Post-discovery measurement of Higgs spin/parity (0+) and couplings; discussion of electroweak vacuum (meta)stability given the measured m_H and top-quark mass m_t",
        "Higgs self-coupling lambda; renormalization-group running of lambda; effective potential V_eff(phi)",
        "RG beta function for lambda", None,
        "vacuum (meta)stability analysis as a limiting/asymptotic statement about V_eff at high field values",
        "measured m_H=125.09+/-0.24 GeV, m_t=173.34+/-0.76 GeV (values as reported in this chapter) used as RG boundary conditions",
        "standard effective-potential convention",
        "Standard Model vacuum lies close to the boundary between stability and metastability",
        "m_H, m_t measurements as above", "electroweak vacuum (meta)stability is not fully resolved observationally", None, ellis_meta)
    add("LIT-012", "LIT-EGN-HIGGS", "A Historical Profile of the Higgs Boson", "Ellis, Gaillard, Nanopoulos",
        "World Scientific, 2016", "271-274", "14.7", "BSM alternatives and open questions",
        None, None, None,
        "Survey of beyond-Standard-Model alternatives (supersymmetric Higgs sectors, compositeness) and open problems connected to the Higgs (dark matter, baryogenesis, neutrino mass, inflation)",
        None, None, None, None,
        "supersymmetric and composite-Higgs scenarios as alternative UV completions",
        None, "The Higgs discovery does not by itself resolve dark matter, baryogenesis, neutrino-mass generation, or inflationary cosmology",
        None,
        "dark matter identity, baryogenesis mechanism, neutrino mass origin, and inflation model are all explicitly still open per this chapter",
        None, ellis_meta)

    # --- Hashimoto, "Theory of Everything" (rejected source) ---
    add("LIT-013", "LIT-HASHIMOTO-TOE", "Theory of Everything", "Junichi Hashimoto",
        "Journal of Innovations in Energy Science (ScholArena)", "all", "entire document", None,
        None, None, None,
        "REJECTED SOURCE -- see SOURCE_VETTING in REFERENCE_METADATA for full rationale. Central claims: invented units ('Gp', 'Skr'), a self-named free parameter ('Junichi Parameter' J) fitted post-hoc to match known measured values for 9 test objects, and rejection of finite light speed / gauge-boson exchange / Newtonian gravitation via informal, non-rigorous reasoning.",
        "self-defined units Gp, Skr; self-named parameter J; integer n; ad hoc constraint x+y=13",
        "none rigorously defined", "Jn = N_BR x 10^(x+y) (the paper's own central relation, with x+y fixed by post-hoc fitting)",
        None,
        "free parameters n, J chosen AFTER the fact so that computed mass/volume/ionization-energy matches already-known measured values for hydrogen, electron, kilogram prototype, bowling ball, Earth, Moon, Sun, Venus, Jupiter",
        "non-standard, source-internal convention only",
        "author's own 'relational physics' / 'clockwork organism' interpretation, not a mainstream physical interpretation",
        "reverse-fitted, not predictive -- does not constitute independent experimental validation",
        "none genuinely resolved; the paper's own methodology (reverse-fitting free parameters to already-known answers) is the disqualifying issue",
        None, hashimoto_meta)

    return items


# ---------------------------------------------------------------------------
# Part IV -- LITERATURE_MDCL_CROSSWALK.csv  (literature item -> MDCL correspondence)
# ---------------------------------------------------------------------------

CROSSWALK_ROWS = [
    dict(LITERATURE_ITEM_ID="LIT-001", SOURCE_ID="LIT-TONG-SM", MDCL_NODE_ID="n/a (scope statement only)",
         MDCL_BRANCH_ID="Gauge/SM (general)", DEPENDENCY_MATCH="UNDETERMINED", NOTATION_MATCH="UNDETERMINED",
         STRUCTURAL_MATCH="NONE", DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-002", SOURCE_ID="LIT-TONG-SM", MDCL_NODE_ID="NOETHER-SYMMETRY (not registered)",
         MDCL_BRANCH_ID="Symmetry", DEPENDENCY_MATCH="ANALOGOUS", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="EXACT (Lorentz/Poincare group structure is the standard continuous-symmetry group any Noether construction on this compiler's fields would need)",
         DERIVATION_MATCH="NONE (source states the group structure; does not derive a UOC-specific current)",
         IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-003", SOURCE_ID="LIT-TONG-SM", MDCL_NODE_ID="QUANTUM-NODE",
         MDCL_BRANCH_ID="Quantum", DEPENDENCY_MATCH="ANALOGOUS", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="ANALOGOUS (Weyl/Dirac spinor representations are the standard relativistic-QM matter-field structure; this compiler's QUANTUM-NODE has no field content at all yet to compare against)",
         DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-004", SOURCE_ID="LIT-TONG-SM", MDCL_NODE_ID="n/a (no discrete-symmetry node exists anywhere in the MDCL)",
         MDCL_BRANCH_ID="Symmetry", DEPENDENCY_MATCH="NONE", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="NONE", DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-005", SOURCE_ID="LIT-TONG-SM", MDCL_NODE_ID="n/a (no discrete-symmetry node exists anywhere in the MDCL)",
         MDCL_BRANCH_ID="Symmetry", DEPENDENCY_MATCH="NONE", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="NONE", DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-006", SOURCE_ID="LIT-TONG-SM", MDCL_NODE_ID="GAUGE-NODE, MATTER-NODE (topics only, not extracted)",
         MDCL_BRANCH_ID="Gauge/SM", DEPENDENCY_MATCH="UNDETERMINED", NOTATION_MATCH="UNDETERMINED",
         STRUCTURAL_MATCH="UNDETERMINED (content not available for comparison)", DERIVATION_MATCH="UNDETERMINED",
         IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-007", SOURCE_ID="LIT-EGN-HIGGS", MDCL_NODE_ID="GAUGE-NODE",
         MDCL_BRANCH_ID="Gauge/SM", DEPENDENCY_MATCH="ANALOGOUS", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="PARTIAL (SSB structure is standard, but GAUGE-NODE has no field/potential content registered to compare against)",
         DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-008", SOURCE_ID="LIT-EGN-HIGGS", MDCL_NODE_ID="GAUGE-NODE",
         MDCL_BRANCH_ID="Gauge/SM", DEPENDENCY_MATCH="ANALOGOUS", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="PARTIAL (Higgs mechanism is the standard mass-generation structure a future GAUGE-NODE implementation would need; nothing currently registered to compare against)",
         DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-009", SOURCE_ID="LIT-EGN-HIGGS", MDCL_NODE_ID="GAUGE-NODE, MATTER-NODE",
         MDCL_BRANCH_ID="Gauge/SM", DEPENDENCY_MATCH="ANALOGOUS", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="PARTIAL", DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-010", SOURCE_ID="LIT-EGN-HIGGS", MDCL_NODE_ID="OBSERVABLES-NODE",
         MDCL_BRANCH_ID="Gauge/SM (observational)", DEPENDENCY_MATCH="NONE", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="NONE (historical/experimental narrative, not a mathematical structure to match against an unexecuted node)",
         DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-011", SOURCE_ID="LIT-EGN-HIGGS", MDCL_NODE_ID="GAUGE-NODE",
         MDCL_BRANCH_ID="Gauge/SM", DEPENDENCY_MATCH="ANALOGOUS", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="PARTIAL (RG-running effective potential is a standard structure; nothing registered here)",
         DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-012", SOURCE_ID="LIT-EGN-HIGGS", MDCL_NODE_ID="COSMOLOGY-NODE (Early-universe)",
         MDCL_BRANCH_ID="Early-universe/Cosmology", DEPENDENCY_MATCH="ANALOGOUS", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="NONE (topically adjacent only -- inflation/vacuum-stability mentioned, no Friedmann-equation structure supplied)",
         DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
    dict(LITERATURE_ITEM_ID="LIT-013", SOURCE_ID="LIT-HASHIMOTO-TOE", MDCL_NODE_ID="EXCLUDED -- REJECTED SOURCE",
         MDCL_BRANCH_ID="EXCLUDED", DEPENDENCY_MATCH="NONE", NOTATION_MATCH="NONE",
         STRUCTURAL_MATCH="NONE", DERIVATION_MATCH="NONE", IMPLEMENTATION_MATCH="NONE", VALIDATION_MATCH="NONE"),
]


# ---------------------------------------------------------------------------
# Part V -- LITERATURE_IMPLEMENTATION_CROSSWALK.csv
# ---------------------------------------------------------------------------

IMPLEMENTATION_CROSSWALK_ROWS = [
    dict(SOURCE_ID="LIT-TONG-SM", LITERATURE_ITEM_ID="LIT-002", MDCL_NODE_ID="NOETHER-SYMMETRY",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP -- literature supplies group structure only, repository supplies nothing"),
    dict(SOURCE_ID="LIT-TONG-SM", LITERATURE_ITEM_ID="LIT-003", MDCL_NODE_ID="QUANTUM-NODE",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP -- repository's only Quantum-branch content is the unrelated eigenvalue-uniqueness counterexample"),
    dict(SOURCE_ID="LIT-TONG-SM", LITERATURE_ITEM_ID="LIT-004", MDCL_NODE_ID="n/a (no node exists)",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP -- no discrete-symmetry node exists to compare against"),
    dict(SOURCE_ID="LIT-TONG-SM", LITERATURE_ITEM_ID="LIT-005", MDCL_NODE_ID="n/a (no node exists)",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP -- no discrete-symmetry node exists to compare against"),
    dict(SOURCE_ID="LIT-EGN-HIGGS", LITERATURE_ITEM_ID="LIT-007", MDCL_NODE_ID="GAUGE-NODE",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP -- GAUGE-NODE is a bare OPEN template node"),
    dict(SOURCE_ID="LIT-EGN-HIGGS", LITERATURE_ITEM_ID="LIT-008", MDCL_NODE_ID="GAUGE-NODE",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP"),
    dict(SOURCE_ID="LIT-EGN-HIGGS", LITERATURE_ITEM_ID="LIT-009", MDCL_NODE_ID="GAUGE-NODE",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP"),
    dict(SOURCE_ID="LIT-EGN-HIGGS", LITERATURE_ITEM_ID="LIT-011", MDCL_NODE_ID="GAUGE-NODE",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP"),
    dict(SOURCE_ID="LIT-EGN-HIGGS", LITERATURE_ITEM_ID="LIT-012", MDCL_NODE_ID="COSMOLOGY-NODE (Early-universe)",
         DEFINITION_PRESENT="NO", DERIVATION_PRESENT="NO", CODE_PRESENT="NO", TEST_PRESENT="NO",
         NUMERICAL_VALIDATION_PRESENT="NO", EXTERNAL_VALIDATION_PRESENT="NO", PROVENANCE_PRESENT="NO",
         DEPENDENCY_COMPLETE="NO", STATUS="GAP -- topically adjacent only, no structural content to compare"),
    dict(SOURCE_ID="LIT-HASHIMOTO-TOE", LITERATURE_ITEM_ID="LIT-013", MDCL_NODE_ID="EXCLUDED",
         DEFINITION_PRESENT="n/a", DERIVATION_PRESENT="n/a", CODE_PRESENT="n/a", TEST_PRESENT="n/a",
         NUMERICAL_VALIDATION_PRESENT="n/a", EXTERNAL_VALIDATION_PRESENT="n/a", PROVENANCE_PRESENT="n/a",
         DEPENDENCY_COMPLETE="n/a", STATUS="EXCLUDED -- REJECTED SOURCE, not eligible for crosswalk use per Part I.3"),
]


# ---------------------------------------------------------------------------
# Part VI -- BRANCH_RECOVERY_MAP.csv
# ---------------------------------------------------------------------------

RECOVERY_MAP_ROWS = [
    dict(BRANCH_ID="Symmetry", REQUIRED_MATHEMATICAL_OBJECT="Lorentz/Poincare symmetry group acting on the field content of VARIATIONAL-NODE",
         REQUIRED_OPERATOR="Generators M^{mu nu}, P^mu", REQUIRED_EQUATION="Noether current J^mu = (dL/d(d_mu phi)) delta phi - K^mu",
         UPSTREAM_DEPENDENCY="VARIATIONAL-NODE (OPEN)", DOWNSTREAM_DEPENDENCY="Conservation",
         SOURCE_ID="LIT-TONG-SM", SOURCE_PAGE="9-15", SOURCE_SECTION="1.1",
         EXTERNAL_STANDARD_STATUS="ESTABLISHED (textbook)", CURRENT_REPOSITORY_STATUS="NOT REGISTERED",
         IMPLEMENTATION_GAP="Group-action structure supplied by literature; UOC-specific action functional and Noether-current construction not supplied by literature or repository",
         INDEPENDENT_REEXECUTION_REQUIRED="YES -- deriving a Noether current for this compiler's own (not-yet-existent) action functional is new work, not a literature lookup"),
    dict(BRANCH_ID="Gauge/Standard Model", REQUIRED_MATHEMATICAL_OBJECT="Gauge field A_mu; Higgs doublet phi",
         REQUIRED_OPERATOR="Covariant derivative D_mu = partial_mu - ig A_mu", REQUIRED_EQUATION="Higgs mechanism mass term m_A^2 = g^2 v^2/4 from |D_mu phi|^2 after SSB",
         UPSTREAM_DEPENDENCY="QUANTUM-NODE (OPEN)", DOWNSTREAM_DEPENDENCY="MATTER-NODE",
         SOURCE_ID="LIT-EGN-HIGGS; LIT-TONG-SM", SOURCE_PAGE="257-263 (Ellis et al); TOC only (Tong Ch.5, not extracted)",
         SOURCE_SECTION="14.2-14.3 (Ellis et al)", EXTERNAL_STANDARD_STATUS="ESTABLISHED (textbook + Nobel-recognized physics)",
         CURRENT_REPOSITORY_STATUS="OPEN (bare template node, no gauge field content of any kind)",
         IMPLEMENTATION_GAP="Standard electroweak Higgs mechanism is well-documented externally, but GAUGE-NODE has no prior gauge-field or matter-field content in this compiler to attach it to -- QUANTUM-NODE must close first",
         INDEPENDENT_REEXECUTION_REQUIRED="YES -- constructing this compiler's own gauge sector, even using the standard SU(2)xU(1) structure, is new implementation work"),
    dict(BRANCH_ID="Geometry", REQUIRED_MATHEMATICAL_OBJECT="Metric tensor g_munu, affine connection",
         REQUIRED_OPERATOR="Covariant derivative nabla_mu; Riemann tensor R^rho_sigmamunu",
         REQUIRED_EQUATION="R_munu = R^rho_murhonu (Ricci contraction); R = g^munu R_munu (scalar curvature)",
         UPSTREAM_DEPENDENCY="SPECTRUM-NODE (OPEN)", DOWNSTREAM_DEPENDENCY="GR",
         SOURCE_ID="none in this corpus", SOURCE_PAGE="n/a", SOURCE_SECTION="n/a",
         EXTERNAL_STANDARD_STATUS="ESTABLISHED (textbook, external to this corpus -- e.g. Wald, MTW; not present in any of the 3 supplied documents)",
         CURRENT_REPOSITORY_STATUS="OPEN (bare template node)",
         IMPLEMENTATION_GAP="No differential-geometry/GR reference exists anywhere in the currently ingested corpus",
         INDEPENDENT_REEXECUTION_REQUIRED="YES, and a differential-geometry reference source is needed before any recovery record can be written for this branch"),
    dict(BRANCH_ID="GR", REQUIRED_MATHEMATICAL_OBJECT="Stress-energy tensor T_munu, cosmological constant Lambda",
         REQUIRED_OPERATOR="Einstein tensor G_munu = R_munu - (1/2) g_munu R",
         REQUIRED_EQUATION="G_munu + Lambda g_munu = (8 pi G/c^4) T_munu",
         UPSTREAM_DEPENDENCY="GEOMETRY-NODE (OPEN), MATTER-NODE (OPEN)", DOWNSTREAM_DEPENDENCY="Quantum/Gravity Interface",
         SOURCE_ID="none in this corpus", SOURCE_PAGE="n/a", SOURCE_SECTION="n/a",
         EXTERNAL_STANDARD_STATUS="ESTABLISHED (textbook, external to this corpus)",
         CURRENT_REPOSITORY_STATUS="OPEN (only SEMICLASSICAL-EINSTEIN-EQUATION, PROPOSED, bulk-imported prose)",
         IMPLEMENTATION_GAP="Same as Geometry -- no GR reference exists in this corpus",
         INDEPENDENT_REEXECUTION_REQUIRED="YES, blocked on Geometry"),
    dict(BRANCH_ID="Thermodynamics", REQUIRED_MATHEMATICAL_OBJECT="Internal energy density e, entropy current S^mu, heat flux q^mu",
         REQUIRED_OPERATOR="grad^mu (spatial gradient projector)", REQUIRED_EQUATION="Clausius-Duhem inequality; q^mu = -kappa grad^mu T, kappa>=0",
         UPSTREAM_DEPENDENCY="MATTER-NODE (OPEN)", DOWNSTREAM_DEPENDENCY="COSMOLOGY-NODE",
         SOURCE_ID="none in this corpus", SOURCE_PAGE="n/a", SOURCE_SECTION="n/a",
         EXTERNAL_STANDARD_STATUS="ESTABLISHED (textbook, external to this corpus)",
         CURRENT_REPOSITORY_STATUS="OPEN (bare template node)",
         IMPLEMENTATION_GAP="No thermodynamics reference exists in this corpus",
         INDEPENDENT_REEXECUTION_REQUIRED="YES, and a relativistic-thermodynamics reference source is needed"),
    dict(BRANCH_ID="Cosmology", REQUIRED_MATHEMATICAL_OBJECT="Scale factor a(t), Hubble parameter H(t), energy density rho, pressure p",
         REQUIRED_OPERATOR="d/dt (cosmic time derivative)", REQUIRED_EQUATION="Friedmann equations H^2 = (8 pi G/3) rho - k/a^2 + Lambda/3",
         UPSTREAM_DEPENDENCY="THERMODYNAMICS-NODE (OPEN)", DOWNSTREAM_DEPENDENCY="OBSERVABLES-NODE",
         SOURCE_ID="LIT-EGN-HIGGS (topically adjacent only)", SOURCE_PAGE="271-274", SOURCE_SECTION="14.7",
         EXTERNAL_STANDARD_STATUS="ESTABLISHED (textbook Friedmann equations are external to this corpus; only vacuum-stability/inflation implications are discussed in the supplied Ellis et al chapter, not the equations themselves)",
         CURRENT_REPOSITORY_STATUS="OPEN (bare template node); FC005_cosmology.yaml exists only as an externally-sourced fiducial-parameter INPUT file to the frozen DESI pipeline, not a derived evolution equation",
         IMPLEMENTATION_GAP="No Friedmann-equation derivation exists in this corpus or this repository",
         INDEPENDENT_REEXECUTION_REQUIRED="YES, and a cosmology reference source deriving the Friedmann equations is needed"),
]


# ---------------------------------------------------------------------------
# Part IX -- L0_RECOVERY_PRIORITY_MATRIX.csv
# ---------------------------------------------------------------------------

PRIORITY_MATRIX_ROWS = [
    dict(NODE_ID="VARIATIONAL-NODE", BRANCH_ID="Variational", DEPENDENCY_DEPTH=2,
         UPSTREAM_REQUIREMENTS="SPECTRUM-NODE (OPEN)", DOWNSTREAM_IMPACT=9,
         LITERATURE_SUPPORT="PARTIAL", IMPLEMENTATION_DIFFICULTY="HIGH (requires constructing an action functional with no literature-supplied bridge from SPECTRUM-NODE)",
         VALIDATION_REQUIREMENT="dimensional consistency; stationarity check delta S=0; limiting-case comparison to a known free-field theory",
         PRIORITY=1),
    dict(NODE_ID="GEOMETRY-NODE", BRANCH_ID="Geometry", DEPENDENCY_DEPTH=2,
         UPSTREAM_REQUIREMENTS="SPECTRUM-NODE (OPEN)", DOWNSTREAM_IMPACT=2,
         LITERATURE_SUPPORT="NONE-IN-CORPUS", IMPLEMENTATION_DIFFICULTY="HIGH, and blocked pending a differential-geometry reference source not yet ingested",
         VALIDATION_REQUIREMENT="metric signature consistency; Bianchi identity; Newtonian limit",
         PRIORITY=2),
    dict(NODE_ID="NOETHER-SYMMETRY", BRANCH_ID="Symmetry", DEPENDENCY_DEPTH=3,
         UPSTREAM_REQUIREMENTS="VARIATIONAL-NODE (OPEN)", DOWNSTREAM_IMPACT=1,
         LITERATURE_SUPPORT="PARTIAL (Lorentz/Poincare structure EXACT; Noether-theorem derivation itself not observed in delivered pages)",
         IMPLEMENTATION_DIFFICULTY="MEDIUM once VARIATIONAL-NODE closes",
         VALIDATION_REQUIREMENT="current conservation d_mu J^mu=0 as a direct consequence check",
         PRIORITY=3),
    dict(NODE_ID="QUANTUM-NODE", BRANCH_ID="Quantum", DEPENDENCY_DEPTH=3,
         UPSTREAM_REQUIREMENTS="VARIATIONAL-NODE (OPEN)", DOWNSTREAM_IMPACT=4,
         LITERATURE_SUPPORT="ANALOGOUS (Weyl/Dirac spinor representations)",
         IMPLEMENTATION_DIFFICULTY="HIGH (canonical quantization map not supplied by literature)",
         VALIDATION_REQUIREMENT="[x,p] canonical commutation check; classical limit hbar->0",
         PRIORITY=4),
    dict(NODE_ID="CONSERVATION-LAW", BRANCH_ID="Conservation", DEPENDENCY_DEPTH=4,
         UPSTREAM_REQUIREMENTS="NOETHER-SYMMETRY (not registered)", DOWNSTREAM_IMPACT=0,
         LITERATURE_SUPPORT="PARTIAL", IMPLEMENTATION_DIFFICULTY="LOW once NOETHER-SYMMETRY exists (direct corollary)",
         VALIDATION_REQUIREMENT="direct numerical/symbolic check that d_mu J^mu=0 for the constructed current",
         PRIORITY=5),
    dict(NODE_ID="GAUGE-NODE", BRANCH_ID="Gauge/Standard Model", DEPENDENCY_DEPTH=4,
         UPSTREAM_REQUIREMENTS="QUANTUM-NODE (OPEN)", DOWNSTREAM_IMPACT=3,
         LITERATURE_SUPPORT="PARTIAL/EXACT (strongest literature support of any zero-backend branch: Tong Yang-Mills structure + Ellis et al SSB/Higgs mechanism)",
         IMPLEMENTATION_DIFFICULTY="HIGH, blocked on Quantum",
         VALIDATION_REQUIREMENT="gauge invariance check; mass-term dimensional consistency; Abelian-limit reduction",
         PRIORITY=6),
    dict(NODE_ID="EINSTEIN-FIELD-EQUATION", BRANCH_ID="GR", DEPENDENCY_DEPTH=3,
         UPSTREAM_REQUIREMENTS="GEOMETRY-NODE (OPEN), MATTER-NODE (OPEN)", DOWNSTREAM_IMPACT=1,
         LITERATURE_SUPPORT="NONE-IN-CORPUS", IMPLEMENTATION_DIFFICULTY="HIGH, blocked on Geometry and Matter",
         VALIDATION_REQUIREMENT="Bianchi identity nabla^mu G_munu=0; Newtonian limit; conservation nabla^mu T_munu=0",
         PRIORITY=7),
    dict(NODE_ID="MATTER-NODE", BRANCH_ID="Matter", DEPENDENCY_DEPTH=5,
         UPSTREAM_REQUIREMENTS="GAUGE-NODE (OPEN)", DOWNSTREAM_IMPACT=2,
         LITERATURE_SUPPORT="NONE-DIRECT (Ellis et al discusses matter-Higgs coupling qualitatively only)",
         IMPLEMENTATION_DIFFICULTY="HIGH, blocked on Gauge", VALIDATION_REQUIREMENT="Yukawa-coupling dimensional consistency",
         PRIORITY=8),
    dict(NODE_ID="THERMODYNAMICS-NODE", BRANCH_ID="Thermodynamic", DEPENDENCY_DEPTH=6,
         UPSTREAM_REQUIREMENTS="MATTER-NODE (OPEN)", DOWNSTREAM_IMPACT=1,
         LITERATURE_SUPPORT="NONE-IN-CORPUS", IMPLEMENTATION_DIFFICULTY="HIGH, and blocked pending a thermodynamics reference source not yet ingested",
         VALIDATION_REQUIREMENT="second-law inequality check (Clausius-Duhem); kappa>=0 positivity",
         PRIORITY=9),
    dict(NODE_ID="INTERFACE-I (Quantum/Gravity)", BRANCH_ID="Quantum/Gravity", DEPENDENCY_DEPTH="blocked (requires both Quantum and GR chains)",
         UPSTREAM_REQUIREMENTS="QUANTUM-NODE (OPEN), GEOMETRY-NODE (OPEN), T2-NCG-BRIDGE (OPEN)", DOWNSTREAM_IMPACT=0,
         LITERATURE_SUPPORT="NONE", IMPLEMENTATION_DIFFICULTY="VERY HIGH (open research problem, not merely an implementation gap)",
         VALIDATION_REQUIREMENT="n/a -- no admissible bridge equation to validate yet",
         PRIORITY=10),
    dict(NODE_ID="COSMOLOGY-NODE (Early-universe)", BRANCH_ID="Early-universe/Cosmology", DEPENDENCY_DEPTH=7,
         UPSTREAM_REQUIREMENTS="THERMODYNAMICS-NODE (OPEN)", DOWNSTREAM_IMPACT=1,
         LITERATURE_SUPPORT="NONE-DIRECT (Ellis et al mentions inflation/vacuum-stability tangentially)",
         IMPLEMENTATION_DIFFICULTY="HIGH, blocked on Thermodynamics; a cosmology reference source is also needed",
         VALIDATION_REQUIREMENT="Friedmann-equation consistency; radiation/matter/Lambda-domination limiting cases",
         PRIORITY=11),
    dict(NODE_ID="COSMOLOGY-NODE (Late-universe)", BRANCH_ID="Late-universe/Cosmology", DEPENDENCY_DEPTH=7,
         UPSTREAM_REQUIREMENTS="THERMODYNAMICS-NODE (OPEN)", DOWNSTREAM_IMPACT=0,
         LITERATURE_SUPPORT="NONE", IMPLEMENTATION_DIFFICULTY="HIGH, blocked on Thermodynamics",
         VALIDATION_REQUIREMENT="dark-energy equation-of-state limiting behavior (w->-1 for Lambda)",
         PRIORITY=12),
    dict(NODE_ID="OBSERVABLES-NODE", BRANCH_ID="Observables (terminal)", DEPENDENCY_DEPTH=8,
         UPSTREAM_REQUIREMENTS="COSMOLOGY-NODE (OPEN)", DOWNSTREAM_IMPACT=0,
         LITERATURE_SUPPORT="NONE", IMPLEMENTATION_DIFFICULTY="depends entirely on everything above closing first",
         VALIDATION_REQUIREMENT="n/a -- terminal node, nothing to validate until upstream closes",
         PRIORITY=13),
]

PRIMITIVE_CHAIN_NOTE_ROWS = [
    dict(NODE_ID=n, BRANCH_ID="Primitive", DEPENDENCY_DEPTH=d,
         UPSTREAM_REQUIREMENTS="SELECTION-SIGMA (OPEN, explicitly unconstructable -- 'no non-arbitrary, unique, representation-invariant derivation of Sigma is registered in this build')",
         DOWNSTREAM_IMPACT="entire template chain", LITERATURE_SUPPORT="NO",
         IMPLEMENTATION_DIFFICULTY="OUT OF SCOPE", VALIDATION_REQUIREMENT="n/a",
         PRIORITY="N/A -- NOT RANKED (out of scope, would require inventing new physics/ontology)")
    for d, n in enumerate(
        ["FOUNDATION", "EMPTYSET", "MATH-UNIVERSE", "PHYSICAL-CANDIDATE-SET", "VACUUM",
         "DISTINCTION", "RELATION", "TRANSFORMATION-NODE", "CONSTRAINT", "PERSISTENCE-NODE",
         "OPERATOR-NODE", "SPECTRUM-NODE"], start=0)
]


# ---------------------------------------------------------------------------
# Part VII -- Proposed Recovery Records
# ---------------------------------------------------------------------------

def build_recovery_records() -> list[dict]:
    return [
        {
            "RECOVERY_ID": "RECOVERY-001",
            "TARGET_NODE": "VARIATIONAL-NODE",
            "SOURCE_REFERENCE": "None of the 3 supplied documents derive an action functional; the variational principle itself is established external mathematics (classical field theory, e.g. Goldstein or any standard QFT text -- NOT among the sources ingested this phase, so this recovery record's REQUIRED_INPUTS below are not literature-sourced and must be treated as a placeholder pending a dedicated classical-mechanics/field-theory source)",
            "SOURCE_DERIVATION": "n/a -- no derivation available in the ingested corpus",
            "REQUIRED_INPUTS": "a field content phi (not yet defined anywhere in this compiler) and a Lagrangian density L(phi, d_mu phi) (not yet defined anywhere in this compiler)",
            "REQUIRED_OPERATORS": "functional derivative delta/delta phi",
            "EXPECTED_OUTPUT": "stationarity condition delta S/delta phi = 0, equivalent to the Euler-Lagrange equations",
            "DEPENDENCIES": "SPECTRUM-NODE (OPEN)",
            "ASSUMPTIONS": "a specific field content and Lagrangian density must be chosen -- this compiler currently supplies neither, and none of the ingested literature supplies UOC-specific choices (only generic textbook machinery)",
            "IMPLEMENTATION_REQUIREMENTS": "symbolic (sympy) construction of a candidate Lagrangian and its Euler-Lagrange equations, analogous in code style to the existing Fisher-information symbolic derivation (compiler/verification/fisher_information.py)",
            "TEST_REQUIREMENTS": "verify delta S=0 reproduces the Euler-Lagrange equation for at least one known free-field case (e.g. a free scalar) as a limiting-case sanity check",
            "FALSIFICATION_REQUIREMENTS": "show the constructed stationarity condition is NOT dimensionally consistent, or does not reduce to a known free-field EL equation in the appropriate limit",
            "CANONICAL_STATUS": "PROPOSED",
        },
        {
            "RECOVERY_ID": "RECOVERY-002",
            "TARGET_NODE": "NOETHER-SYMMETRY",
            "SOURCE_REFERENCE": "LIT-002 (Tong, 'The Standard Model', section 1.1, pp. 9-15)",
            "SOURCE_DERIVATION": "Lorentz group SO(3,1)/Poincare group structure, generators M^{mu nu}, P^mu, as the continuous spacetime symmetry group of any relativistic field theory",
            "REQUIRED_INPUTS": "VARIATIONAL-NODE must be CLOSED first (a concrete Lagrangian L(phi, d_mu phi) is required to compute a Noether current)",
            "REQUIRED_OPERATORS": "infinitesimal symmetry generator delta phi; canonical energy-momentum-like current construction dL/d(d_mu phi)",
            "EXPECTED_OUTPUT": "conserved current J^mu satisfying d_mu J^mu = 0 on-shell",
            "DEPENDENCIES": "VARIATIONAL-NODE (OPEN, must close first)",
            "ASSUMPTIONS": "the field content is assumed to transform in a representation of the Poincare group per LIT-002's structure",
            "IMPLEMENTATION_REQUIREMENTS": "symbolic construction of J^mu from the closed VARIATIONAL-NODE's Lagrangian, following the standard Noether-current formula",
            "TEST_REQUIREMENTS": "numerically or symbolically verify d_mu J^mu = 0 using the field equations from VARIATIONAL-NODE",
            "FALSIFICATION_REQUIREMENTS": "show d_mu J^mu != 0 off a measure-zero set, or show the claimed symmetry is not in fact a symmetry of the constructed Lagrangian",
            "CANONICAL_STATUS": "PROPOSED",
        },
        {
            "RECOVERY_ID": "RECOVERY-003",
            "TARGET_NODE": "GAUGE-NODE",
            "SOURCE_REFERENCE": "LIT-007, LIT-008, LIT-009, LIT-011 (Ellis, Gaillard, Nanopoulos, 'A Historical Profile of the Higgs Boson', sections 14.2-14.3, 14.6, pp. 257-263, 268-271)",
            "SOURCE_DERIVATION": "Higgs mechanism: SSB of a local gauge symmetry via a scalar doublet phi with potential V(phi), gauge-boson mass generation from |D_mu phi|^2, applied to SU(2)xU(1) electroweak unification",
            "REQUIRED_INPUTS": "QUANTUM-NODE must be CLOSED first (a Hilbert-space/field-quantization structure is required before a gauge symmetry can act on it)",
            "REQUIRED_OPERATORS": "covariant derivative D_mu = partial_mu - ig A_mu; scalar potential V(phi) = -mu^2|phi|^2 + lambda|phi|^4",
            "EXPECTED_OUTPUT": "gauge-boson mass term m_A^2 = g^2 v^2/4 after SSB, and the residual unbroken-symmetry structure (e.g. massless photon in the electroweak case)",
            "DEPENDENCIES": "QUANTUM-NODE (OPEN, must close first)",
            "ASSUMPTIONS": "a specific gauge group and representation content must be chosen for this compiler -- LIT-007/008/009/011 supply the standard SU(2)xU(1) electroweak case as the best-attested external template, but choosing it for THIS compiler's own matter content is a new decision, not something the literature makes for us",
            "IMPLEMENTATION_REQUIREMENTS": "symbolic construction of the covariant derivative, potential, and mass term following the standard construction; explicit gauge-invariance check of the full Lagrangian",
            "TEST_REQUIREMENTS": "verify gauge invariance under a general gauge transformation; verify the mass term reduces to the known electroweak relation m_W = (1/2) g v in the appropriate parameter limit",
            "FALSIFICATION_REQUIREMENTS": "show the constructed Lagrangian is not gauge invariant, or that the mass spectrum does not match the standard electroweak relations in the appropriate limit",
            "CANONICAL_STATUS": "PROPOSED",
        },
    ]


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main():
    manifest = build_baseline_manifest()
    (ROOT / "L0_BASELINE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote L0_BASELINE_MANIFEST.json (commit {manifest['git_commit']})")

    write_csv(ROOT / "L0_BRANCH_BACKEND_GAP_MATRIX.csv", GAP_MATRIX_ROWS)
    print(f"wrote L0_BRANCH_BACKEND_GAP_MATRIX.csv ({len(GAP_MATRIX_ROWS)} rows)")

    extraction = build_extraction_registry()
    (ROOT / "LITERATURE_EXTRACTION_REGISTRY.json").write_text(json.dumps(extraction, indent=2) + "\n")
    print(f"wrote LITERATURE_EXTRACTION_REGISTRY.json ({len(extraction)} items)")

    write_csv(ROOT / "LITERATURE_MDCL_CROSSWALK.csv", CROSSWALK_ROWS)
    print(f"wrote LITERATURE_MDCL_CROSSWALK.csv ({len(CROSSWALK_ROWS)} rows)")

    write_csv(ROOT / "LITERATURE_IMPLEMENTATION_CROSSWALK.csv", IMPLEMENTATION_CROSSWALK_ROWS)
    print(f"wrote LITERATURE_IMPLEMENTATION_CROSSWALK.csv ({len(IMPLEMENTATION_CROSSWALK_ROWS)} rows)")

    write_csv(ROOT / "BRANCH_RECOVERY_MAP.csv", RECOVERY_MAP_ROWS)
    print(f"wrote BRANCH_RECOVERY_MAP.csv ({len(RECOVERY_MAP_ROWS)} rows)")

    write_csv(ROOT / "L0_RECOVERY_PRIORITY_MATRIX.csv", PRIORITY_MATRIX_ROWS + PRIMITIVE_CHAIN_NOTE_ROWS)
    print(f"wrote L0_RECOVERY_PRIORITY_MATRIX.csv ({len(PRIORITY_MATRIX_ROWS) + len(PRIMITIVE_CHAIN_NOTE_ROWS)} rows)")

    records_dir = ROOT / "L0_PROPOSED_RECOVERY_RECORDS"
    records_dir.mkdir(exist_ok=True)
    for rec in build_recovery_records():
        p = records_dir / f"{rec['RECOVERY_ID']}.json"
        p.write_text(json.dumps(rec, indent=2) + "\n")
        print(f"wrote {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
