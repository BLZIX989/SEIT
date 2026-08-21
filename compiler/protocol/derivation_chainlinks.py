"""Phase 12 first execution task (master brief section XXXVIII): identify
the chainlinks in the project's conceptual Delta -> Gamma -> G -> L ->
Spec(L) -> g_mu_nu -> ... chain that this compiler can ALREADY execute
without inventing missing mathematics, and represent them as explicit,
individually-tracked Chainlink records -- then honestly record the first
real obstruction where the chain currently stops.

Every Chainlink built here is a projection over IR nodes/Transformations
`compiler.ir.executable_tests.register_executable_tests()` already
registered and ran for real (Test 1: graph -> Laplacian -> spectrum ->
heat flow -> kernel projector; Test 2: spectrum -> diffusion distance ->
candidate metric). Nothing here re-executes or re-derives anything --
this module only reads `t.status`, `t.proof`, `t.dependencies` off the
already-built registries and classifies them.

The `reproducibility` classification for each of the 6 real chainlinks
below is a one-time, hand-written summary of that specific transformation's
own `proof`/`verification` text at the time this module was written (see
compiler/ir/executable_tests.py) -- not a generic auto-classifier, since
auto-classifying free-text "proof" strings would itself be a fabrication
risk for a field whose entire purpose is precision about what was actually
shown.
"""
from __future__ import annotations

from compiler.core.status import Status
from compiler.falsification.protocols import FalsificationRecord
from compiler.ir.registry import MDCLRegistries
from compiler.protocol.registry import ChainlinkRegistry
from compiler.protocol.schema import Chainlink

# transformation_id -> hand-classified reproducibility, derived from that
# transformation's own real `proof` text in executable_tests.py /
# discrete_curvature.py.
_REPRODUCIBILITY = {
    "T-GRAPH-TO-OPERATOR": "EXACT_DEFINITIONAL",              # L=D-A read directly off edge set
    "T-OPERATOR-TO-SPECTRUM": "NUMERIC_WITH_EXACT_CROSSCHECK_N<=8",
    "T-SPECTRUM-TO-HEATFLOW": "NUMERIC_TOLERANCE_1E-6",
    "T-HEATFLOW-TO-KERNEL": "NUMERIC_TOLERANCE_1E-6",
    "T-SPECTRUM-TO-DIFFUSION": "EXACT_DEFINITIONAL",           # direct formula evaluation
    "T-DIFFUSION-TO-METRIC": "NUMERIC_NON_UNIQUE",             # depends on free diffusion-time parameter
    "T-OPERATOR-TO-CURVATURE": "NUMERIC_WITH_LP_DUALITY_CROSSCHECK",
    "T-LICHNEROWICZ-GAUGE-TERM": "EXACT_SYMBOLIC_ZERO_RESIDUAL",
    "T-LICHNEROWICZ-GRAVITY-TERM": "EXACT_SYMBOLIC_COEFFICIENT_SOLVED",
    "T-SEELEY-DEWITT-A0-A2-A4-NUMERIC": "NUMERIC_TOLERANCE_1E-4_AT_4_DISTINCT_E_VALUES",
    "T-FINITE-SPECTRAL-TRIPLE-AXIOMS": "NUMERIC_N=200_PLUS_SYMBOLIC_GENERAL_CROSSCHECK_N=4",
    "T-DIRAC-SQUARED-FINITE": "EXACT_NUMERIC_BLOCK_MATCH",
    "T-FINITE-SPECTRAL-TRIPLE-RECOVERY-AXIOMS": "NUMERIC_N=200_COMPLEX_PLUS_SYMBOLIC_GENERAL_CROSSCHECK_N=4",
}

# transformation_id -> whether a genuine symbolic/definitional proof backs
# it (vs. numeric verification only). T-GRAPH-TO-OPERATOR and
# T-SPECTRUM-TO-DIFFUSION are direct evaluations of a definition -- there is
# nothing to numerically approximate. The rest are numerically verified
# per-case, with T-OPERATOR-TO-SPECTRUM additionally cross-checked exactly
# (sympy) for n<=8, and T-OPERATOR-TO-CURVATURE hand-verified for 2 specific
# edges against the definition directly (not just internal LP
# self-consistency); neither partial check makes it a general proof.
_PROOF_STATUS = {
    "T-GRAPH-TO-OPERATOR": "PROVEN_DEFINITIONAL",
    "T-OPERATOR-TO-SPECTRUM": "NUMERIC_VERIFICATION_ONLY",
    "T-SPECTRUM-TO-HEATFLOW": "NUMERIC_VERIFICATION_ONLY",
    "T-HEATFLOW-TO-KERNEL": "NUMERIC_VERIFICATION_ONLY",
    "T-SPECTRUM-TO-DIFFUSION": "PROVEN_DEFINITIONAL",
    "T-DIFFUSION-TO-METRIC": "NO_PROOF_REGISTERED",
    "T-OPERATOR-TO-CURVATURE": "NUMERIC_WITH_HAND_VERIFIED_CASES",
    "T-LICHNEROWICZ-GAUGE-TERM": "PROVEN_SYMBOLIC_EXACT",
    "T-LICHNEROWICZ-GRAVITY-TERM": "PROVEN_SYMBOLIC_EXACT",
    "T-SEELEY-DEWITT-A0-A2-A4-NUMERIC": "NUMERIC_VERIFICATION_ONLY",
    "T-FINITE-SPECTRAL-TRIPLE-AXIOMS": "PROVEN_SYMBOLIC_GENERAL_FOR_FIRST_ORDER_CONDITION_PLUS_NUMERIC",
    "T-DIRAC-SQUARED-FINITE": "PROVEN_DEFINITIONAL",
    "T-FINITE-SPECTRAL-TRIPLE-RECOVERY-AXIOMS": "PROVEN_SYMBOLIC_GENERAL_FOR_FIRST_ORDER_CONDITION_PLUS_NUMERIC",
}

# transformation_id -> real backend module that executes it.
_EXECUTABLE_BACKEND = {
    "T-GRAPH-TO-OPERATOR": "compiler/backends/pipeline_graph_heatflow.py",
    "T-OPERATOR-TO-SPECTRUM": "compiler/backends/pipeline_graph_heatflow.py",
    "T-SPECTRUM-TO-HEATFLOW": "compiler/backends/pipeline_graph_heatflow.py",
    "T-HEATFLOW-TO-KERNEL": "compiler/backends/pipeline_graph_heatflow.py",
    "T-SPECTRUM-TO-DIFFUSION": "compiler/backends/diffusion_metric.py",
    "T-DIFFUSION-TO-METRIC": "compiler/backends/diffusion_metric.py",
    "T-OPERATOR-TO-CURVATURE": "compiler/backends/ollivier_ricci.py",
    "T-LICHNEROWICZ-GAUGE-TERM": "compiler/backends/lichnerowicz_seeley_dewitt.py",
    "T-LICHNEROWICZ-GRAVITY-TERM": "compiler/backends/lichnerowicz_seeley_dewitt.py",
    "T-SEELEY-DEWITT-A0-A2-A4-NUMERIC": "compiler/backends/lichnerowicz_seeley_dewitt.py",
    "T-FINITE-SPECTRAL-TRIPLE-AXIOMS": "compiler/backends/finite_spectral_triple_candidate.py",
    "T-DIRAC-SQUARED-FINITE": "compiler/backends/finite_spectral_triple_candidate.py",
    "T-FINITE-SPECTRAL-TRIPLE-RECOVERY-AXIOMS": "compiler/backends/finite_spectral_triple_recovery.py",
}

# (chainlink_id, transformation_id, mathematical_statement)
_REAL_CHAINLINKS = [
    ("CL-G-TO-L", "T-GRAPH-TO-OPERATOR", "L = D - A for graph G=(V,E)"),
    ("CL-L-TO-SPECL", "T-OPERATOR-TO-SPECTRUM", "L phi_n = lambda_n phi_n"),
    ("CL-SPECL-TO-HEATFLOW", "T-SPECTRUM-TO-HEATFLOW", "R(t) = e^{-tL}"),
    ("CL-HEATFLOW-TO-KERNEL", "T-HEATFLOW-TO-KERNEL", "lim_{t->inf} e^{-tL} = P_ker(L)"),
    ("CL-SPECL-TO-DIFFUSION", "T-SPECTRUM-TO-DIFFUSION", "d_t(i,j)^2 = sum_n e^{-2t lambda_n}(phi_n(i)-phi_n(j))^2"),
    ("CL-DIFFUSION-TO-METRIC", "T-DIFFUSION-TO-METRIC", "candidate g_ij from diffusion-distance refinement sweep"),
    ("CL-OPERATOR-TO-CURVATURE-DISCRETE", "T-OPERATOR-TO-CURVATURE",
     "kappa(x,y) = 1 - W1(m_x,m_y)/d(x,y) (Ollivier-Ricci, alpha=0)"),
]

# (chainlink_id, transformation_id, mathematical_statement) -- SAME shape as
# _REAL_CHAINLINKS above, but for transformations registered by
# compiler/ir/seeley_dewitt_verification.py, which (like FC-005) is NOT part
# of the minimal registry compiler/tests/test_protocol_chainlinks.py builds
# for its generic Chainlink-layer tests. Kept as a separate list (rather than
# folded into _REAL_CHAINLINKS, which that test iterates over unconditionally)
# and added below with an explicit "in registries.transformations" guard, the
# same pattern already used for CONTINUUM-LIMIT-L-DESI's conditional
# registration.
_LICHNEROWICZ_SEELEY_DEWITT_CHAINLINKS = [
    ("CL-CONTROL-TO-LICHNEROWICZ-GAUGE", "T-LICHNEROWICZ-GAUGE-TERM",
     "D_A^2 = -(nabla^2+E), E = i*F_12*gamma^1*gamma^2 (flat 2D control, gauge term only)"),
    ("CL-CONTROL-TO-LICHNEROWICZ-GRAVITY", "T-LICHNEROWICZ-GRAVITY-TERM",
     "D^2 = -(nabla^2+E), E = c*R with c solved = -1/4 (round S^2 control, gravity term only)"),
    ("CL-LICHNEROWICZ-TO-SEELEY-DEWITT", "T-SEELEY-DEWITT-A0-A2-A4-NUMERIC",
     "a0=tr(I)*Vol, a2=tr(E+R/6)*Vol, a4=(1/360)tr[60ER+180E^2+5R^2-2Ric^2+2Riem^2]*Vol (S^3 control)"),
]

# Same shape and guard pattern as above, for
# compiler/ir/finite_spectral_triple_certification.py's transformations.
_FINITE_SPECTRAL_TRIPLE_CHAINLINKS = [
    ("CL-CONTROL-TO-FINITE-SPECTRAL-TRIPLE-AXIOMS", "T-FINITE-SPECTRAL-TRIPLE-AXIOMS",
     "self-adjointness, grading, real-structure-sign, and first-order-condition "
     "[[D_F,pi(f)],pi(g)]=0 checks against (A_F,H_F,D_F,J_F,gamma_F) -- FAILS "
     "(first-order condition; exact closed form, generically nonzero)"),
    ("CL-FINITE-DIRAC-SQUARED", "T-DIRAC-SQUARED-FINITE",
     "D_F^2 = diag(d1 d1^T, d1^T d1), exactly block-diagonal, E_B=0 for the bare operator"),
    ("CL-FINITE-SPECTRAL-TRIPLE-RECOVERY", "T-FINITE-SPECTRAL-TRIPLE-RECOVERY-AXIOMS",
     "[[D_F',pi'(f)],J'pi'(g)J'^-1]=0 HOLDS for the doubled (A_F,H_F'=H_F(+)H_F,D_F'=D_F(+)D_F,"
     "J_F',gamma_F') -- recovery after the original candidate's certification FAILED"),
]


# chainlink_id -> real FalsificationRecord id prefixes known (by direct
# code inspection of executable_tests.py / run_compiler.py) to target that
# chainlink's output. Explicit rather than fuzzy-matched on `.target` free
# text: "Spec(L) for cycle(n=10)..." vs "SPECTRUM-L" do not share a
# substring, so a text heuristic silently misses a real match -- explicit
# id mapping is the only honest option for a set this small and fixed.
_FALSIFICATION_ID_PREFIXES = {
    "CL-L-TO-SPECL": ["FALS-SPECTRUM-RELABELING-INVARIANCE"],
    "CL-DIFFUSION-TO-METRIC": ["FALS-METRIC-UNIQUENESS-"],
    "CL-OPERATOR-TO-CURVATURE-DISCRETE": ["FALS-CURVATURE-RELABELING-RIT", "FALS-CURVATURE-RELABELING-MIT"],
}


def _falsification_status(chainlink_id: str, falsifications: list[FalsificationRecord]) -> str:
    prefixes = _FALSIFICATION_ID_PREFIXES.get(chainlink_id, [])
    matches = [f for f in falsifications if any(f.id.startswith(p) for p in prefixes)]
    if not matches:
        return "NOT_TESTED"
    if all(m.passed for m in matches):
        return "TESTED_SURVIVED"
    if any(m.passed for m in matches):
        return "TESTED_PARTIAL_FAILURE"
    return "TESTED_FAILED"


def build_derivation_chainlinks(
    registries: MDCLRegistries, falsifications: list[FalsificationRecord],
) -> ChainlinkRegistry:
    reg = ChainlinkRegistry()

    for chainlink_id, transformation_id, statement in _REAL_CHAINLINKS:
        t = registries.transformations.get(transformation_id)
        status_val = t.status.value if isinstance(t.status, Status) else t.status
        link = Chainlink(
            chainlink_id=chainlink_id,
            source_node=t.domain,
            target_node=t.codomain,
            transformation=t.action,
            mathematical_statement=statement,
            dependencies=list(t.dependencies),
            assumptions=list(t.assumptions),
            status=status_val,
            proof_status=_PROOF_STATUS[transformation_id],
            calculation_status=status_val,
            falsification_status=_falsification_status(chainlink_id, falsifications),
            executable_backend=_EXECUTABLE_BACKEND[transformation_id],
            reproducibility=_REPRODUCIBILITY[transformation_id],
            open_obligations=[] if status_val in ("VERIFIED", "DERIVED", "CALCULATED") else [
                f"{transformation_id} status is {status_val}, not admissible for downstream chainlinks"
            ],
            failure_conditions={
                "T-DIFFUSION-TO-METRIC": ["classification reported as 'non_unique' or 'divergent' "
                                          "for a swept topology"],
                "T-OPERATOR-TO-CURVATURE": ["primal/dual LP duality gap exceeds 1e-6 on any swept edge"],
            }.get(transformation_id, ["numeric residual exceeds registered tolerance",
                                       "sympy exact cross-check disagrees with numeric result (n<=8 cases)"]),
            provenance_source=t.provenance.source if t.provenance else "",
            source_document_status="N/A",
        )
        if chainlink_id == "CL-OPERATOR-TO-CURVATURE-DISCRETE":
            link.assumptions = list(link.assumptions) + [
                "This is an INDEPENDENT route around CL-METRIC-TO-CONNECTION, not a resolution of "
                "it: Ollivier-Ricci curvature is a discrete graph-curvature notion computed directly "
                "from OPERATOR-L's own random-walk structure (established mathematics, Ollivier 2009), "
                "not a continuum Levi-Civita connection built from METRIC-CANDIDATE. "
                "CL-METRIC-TO-CONNECTION remains OPEN.",
            ]
        reg.add(link)

    # Lichnerowicz/Seeley-DeWitt chainlinks: same construction as the loop
    # above, guarded by presence -- compiler/ir/seeley_dewitt_verification.py
    # is not part of the minimal registry
    # compiler/tests/test_protocol_chainlinks.py builds for its generic
    # Chainlink-layer tests (same reason CONTINUUM-LIMIT-L-DESI below is
    # guarded rather than folded into the unconditional loop above).
    for chainlink_id, transformation_id, statement in _LICHNEROWICZ_SEELEY_DEWITT_CHAINLINKS:
        if transformation_id not in registries.transformations:
            continue
        t = registries.transformations.get(transformation_id)
        status_val = t.status.value if isinstance(t.status, Status) else t.status
        reg.add(Chainlink(
            chainlink_id=chainlink_id,
            source_node=t.domain,
            target_node=t.codomain,
            transformation=t.action,
            mathematical_statement=statement,
            dependencies=list(t.dependencies),
            assumptions=list(t.assumptions),
            status=status_val,
            proof_status=_PROOF_STATUS[transformation_id],
            calculation_status=status_val,
            falsification_status="NOT_TESTED",
            executable_backend=_EXECUTABLE_BACKEND[transformation_id],
            reproducibility=_REPRODUCIBILITY[transformation_id],
            open_obligations=[] if status_val in ("VERIFIED", "DERIVED", "CALCULATED") else [
                f"{transformation_id} status is {status_val}, not admissible for downstream chainlinks"
            ],
            failure_conditions=["residual is not exactly/numerically zero against the claimed identity"],
            provenance_source=t.provenance.source if t.provenance else "",
            source_document_status="N/A",
        ))

    # Finite spectral-triple certification chainlinks: same guarded
    # construction as the Lichnerowicz/Seeley-DeWitt loop above.
    for chainlink_id, transformation_id, statement in _FINITE_SPECTRAL_TRIPLE_CHAINLINKS:
        if transformation_id not in registries.transformations:
            continue
        t = registries.transformations.get(transformation_id)
        status_val = t.status.value if isinstance(t.status, Status) else t.status
        reg.add(Chainlink(
            chainlink_id=chainlink_id,
            source_node=t.domain,
            target_node=t.codomain,
            transformation=t.action,
            mathematical_statement=statement,
            dependencies=list(t.dependencies),
            assumptions=list(t.assumptions),
            status=status_val,
            proof_status=_PROOF_STATUS[transformation_id],
            calculation_status=status_val,
            falsification_status="NOT_TESTED",
            executable_backend=_EXECUTABLE_BACKEND[transformation_id],
            reproducibility=_REPRODUCIBILITY[transformation_id],
            open_obligations=[] if status_val in ("VERIFIED", "DERIVED", "CALCULATED") else [
                f"{transformation_id} status is {status_val}, not admissible for downstream chainlinks "
                "-- specifically, this FAIL blocks (E_B,Omega_B) via the standard NCG inner-fluctuation "
                "mechanism, per compiler/historical/finite_spectral_triple_certification.py"
            ],
            failure_conditions=["[[D_F,pi(f)],pi(g)] is not identically zero for the candidate algebra "
                                "representation (exactly what was found here)"],
            provenance_source=t.provenance.source if t.provenance else "",
            source_document_status="N/A",
        ))

    # The honest frontier this certification produces: Omega_B and the
    # finite spectral-action moments a0^B..a6^B are OPEN, not because they
    # were never attempted, but because the certification that would
    # license computing them genuinely FAILS (first-order condition).
    if "SPECTRAL-ACTION-A0-A6-FINITE-B" in registries.objects:
        sa_finite = registries.objects.get("SPECTRAL-ACTION-A0-A6-FINITE-B")
        sa_status = sa_finite.status.value if isinstance(sa_finite.status, Status) else sa_finite.status
        reg.add(Chainlink(
            chainlink_id="CL-FINITE-TRIPLE-TO-SPECTRAL-ACTION",
            source_node="OMEGA_B-FINITE",
            target_node="SPECTRAL-ACTION-A0-A6-FINITE-B",
            transformation="Omega_B (inner-fluctuation curvature) -> a0^B,a2^B,a4^B,a6^B (NOT CERTIFIABLE)",
            mathematical_statement="S_eff^B = Tr f(D_A^B/Lambda) ~ sum_k a_{2k}^B Lambda^{d-2k} + ... "
                                    "(requires a well-posed fluctuated D_A^B, which requires the "
                                    "first-order condition -- FALSE for this candidate)",
            dependencies=["OMEGA_B-FINITE"],
            assumptions=list(sa_finite.assumptions),
            status=sa_status,
            proof_status="OPEN",
            calculation_status=sa_status,
            falsification_status="NOT_TESTED",
            executable_backend=None,
            reproducibility="N/A_NOT_EXECUTED",
            open_obligations=[
                "the first-order condition fails for this candidate's (A_F,J_F) -- see "
                "AXIOM-CHECK-FIRST-ORDER-CONDITION and CL-CONTROL-TO-FINITE-SPECTRAL-TRIPLE-AXIOMS",
                "a genuinely different (A_F,J_F,gamma_F) that passes the first-order condition has "
                "not been found or attempted anywhere in this corpus",
            ],
            failure_conditions=[
                "an alternative candidate is constructed and its own first-order-condition check fails "
                "the same way (would need its own independent certification, not inherited from this one)",
            ],
            provenance_source="compiler/protocol/derivation_chainlinks.py (finite spectral-triple frontier)",
            source_document_status="N/A",
        ))

    # CONTINUUM-LIMIT-L-DESI: unlike the 7 chainlinks above, this edge has no
    # registered Transformation (compiler/ir/fc005.py only registers Objects
    # with dependency links for the DESI chain) -- so this chainlink is
    # computed directly from the real CONTINUUM-LIMIT-L-DESI Object's own
    # status/dependencies/provenance instead, exactly as honest a source as
    # a Transformation would be, and reflects how this branch is actually
    # built rather than inventing a Transformation node to fit the pattern.
    # Added as a first-class chainlink (not a footnote) alongside the
    # FC005-CONTINUUM-EXPONENT-CORRECTION provenance record documenting the
    # eps^(5/2) -> eps^5 exponent correction this node's label carries.
    # Only registered when FC-005 has actually been registered into these
    # registries (register_fc005() is not part of every build path -- e.g.
    # the isolated Phase-12 unit tests build only the graph/curvature
    # chain -- and this chainlink must not claim to describe a node that
    # was never built).
    if "CONTINUUM-LIMIT-L-DESI" in registries.objects:
        continuum = registries.objects.get("CONTINUUM-LIMIT-L-DESI")
        continuum_status = continuum.status.value if isinstance(continuum.status, Status) else continuum.status
        reg.add(Chainlink(
            chainlink_id="CL-OPERATOR-TO-CONTINUUM-DESI",
            source_node="OPERATOR-L-DESI",
            target_node="CONTINUUM-LIMIT-L-DESI",
            transformation="L_tilde_(N,eps) = -L_N / (C_K * N * eps^(d+2)) -- continuum-limit "
                           "normalization applied to the real DESI-derived graph Laplacian",
            mathematical_statement="L_tilde_(N,eps) = -L_N/(C_K N eps^5), d=3",
            dependencies=list(continuum.dependencies),
            assumptions=list(continuum.assumptions) + [
                "eps^(d+2)=eps^5 (d=3) is CORRECTED from the workbook's original eps^(d/2+1)="
                "eps^(5/2) -- see FC005-CONTINUUM-EXPONENT-CORRECTION for the full provenance "
                "record and compiler/backends/desi_graph.py::normalize_continuum_limit for the "
                "derivation.",
            ],
            status=continuum_status,
            proof_status="NUMERIC_VERIFICATION_ONLY",
            calculation_status=continuum_status,
            falsification_status="NOT_TESTED",
            executable_backend="compiler/backends/desi_graph.py::normalize_continuum_limit",
            reproducibility=("NUMERIC_ON_REAL_DESI_PILOT_FIXTURE"
                             if continuum.provenance and
                             continuum.provenance.verification.get("gate1_converged") is not None
                             else "N/A_BLOCKED_ON_DESI_CATALOGUE"),
            open_obligations=[] if continuum_status in ("VERIFIED", "DERIVED", "CALCULATED") else [
                f"CONTINUUM-LIMIT-L-DESI status is {continuum_status}, not admissible for "
                "downstream DESI chainlinks (DESI-SPECTRUM, DESI-HEAT-TRACE, ...)"
            ],
            failure_conditions=["Gate 1 (mathematical convergence) fails on (N,eps) refinement -- "
                                "see MATHEMATICAL-CONVERGENCE-DESI"],
            provenance_source=continuum.provenance.source if continuum.provenance else "",
            source_document_status="N/A",
        ))

    # The honest frontier: this is where the real, executed chain actually
    # stops today. METRIC-CANDIDATE is CONDITIONAL and explicitly
    # non-unique (compiler/backends/diffusion_metric.py's own
    # classification, never "exact") -- there is no canonical,
    # non-arbitrary construction of a Levi-Civita-type connection over a
    # metric that depends on a free parameter (diffusion time t) without
    # either (a) picking t arbitrarily, which the spec's own
    # non-arbitrariness requirement forbids, or (b) applying an
    # established discrete-differential-geometry method (e.g.
    # Ollivier-Ricci curvature, Forman-Ricci curvature) and running it
    # through the real falsification protocols (representation invariance,
    # mathematical invariance) before it could even be registered as
    # PROPOSED. Neither has been attempted in this build. Recording this
    # as OPEN with an explicit obstruction, rather than skipping it or
    # inventing a construction, is the point of Phase 12's audit.
    metric = registries.objects.get("METRIC-CANDIDATE")
    reg.add(Chainlink(
        chainlink_id="CL-METRIC-TO-CONNECTION",
        source_node="METRIC-CANDIDATE",
        target_node="CONNECTION-NODE",
        transformation="Levi-Civita-type connection from candidate metric g_ij (NOT REGISTERED)",
        mathematical_statement="Gamma^k_ij = 1/2 g^kl (d_i g_jl + d_j g_il - d_l g_ij) (continuum form; "
                                "no discrete analogue is registered for this candidate)",
        dependencies=["METRIC-CANDIDATE"],
        assumptions=[
            "METRIC-CANDIDATE's own status is CONDITIONAL with an explicit non-uniqueness finding "
            "(see falsification_registry.json FALS-METRIC-UNIQUENESS-*): the diffusion-distance "
            "candidate depends on a free time parameter t, so there is no single admissible metric "
            "to differentiate.",
        ],
        status="OPEN",
        proof_status="OPEN",
        calculation_status="OPEN",
        falsification_status="NOT_TESTED",
        executable_backend=None,
        reproducibility="N/A_NOT_EXECUTED",
        open_obligations=[
            "no admissible, non-arbitrary construction of a connection from a non-unique metric "
            "candidate is registered in this compiler",
            "CL-OPERATOR-TO-CURVATURE-DISCRETE registers a real Ollivier-Ricci discrete curvature "
            "computed independently of METRIC-CANDIDATE (parameter-free, survives real RIT/MIT "
            "falsification runs) -- but that is a DIFFERENT construction, not a resolution of this "
            "chainlink. This chainlink remains OPEN: no connection has been built FROM "
            "METRIC-CANDIDATE specifically.",
        ],
        failure_conditions=[
            "any candidate connection construction that depends on an arbitrary, unjustified "
            "choice of the diffusion-time parameter t is inadmissible by the same non-arbitrariness "
            "requirement METRIC-CANDIDATE itself was already held to",
        ],
        provenance_source="compiler/protocol/derivation_chainlinks.py (Phase 12 frontier audit)",
        source_document_status="N/A",
    ))

    # The honest frontier of the D_A^2=-(nabla^2+E) -> a0 -> a2 -> a4 -> a6 ->
    # Tr f(D_A/Lambda) -> S_eff chain: a0, a2, a4 are now verified (on
    # control manifolds -- CL-LICHNEROWICZ-TO-SEELEY-DEWITT above), but the
    # general a6 formula was explicitly NOT independently rederived (see
    # compiler/historical/seeley_dewitt_verification.py::A6_SCOPE_NOTE), so
    # Tr f(D_A/Lambda) cannot be certified. Recorded as OPEN with an
    # explicit obstruction, per the same discipline CL-METRIC-TO-CONNECTION
    # above already applies to the geometry branch's own frontier.
    if "SEELEY-DEWITT-A6-GENERAL" in registries.objects:
        a6 = registries.objects.get("SEELEY-DEWITT-A6-GENERAL")
        a6_status = a6.status.value if isinstance(a6.status, Status) else a6.status
        reg.add(Chainlink(
            chainlink_id="CL-SEELEY-DEWITT-TO-SPECTRAL-ACTION",
            source_node="SEELEY-DEWITT-A6-GENERAL",
            target_node="SPECTRAL-ACTION-TR-F-CERTIFICATION",
            transformation="a6 (general Gilkey formula, position-dependent E(x), nonabelian Omega_{mu nu}, "
                           "Delta E, dozen-plus curvature invariants) -> Tr f(D_A/Lambda) (NOT REGISTERED)",
            mathematical_statement="S_eff = Tr f(D_A/Lambda) ~ sum_k a_{2k} Lambda^{d-2k} + ... "
                                    "(requires a6, among others, not yet resolved)",
            dependencies=["SEELEY-DEWITT-A6-GENERAL"],
            assumptions=list(a6.assumptions),
            status=a6_status,
            proof_status="OPEN",
            calculation_status=a6_status,
            falsification_status="NOT_TESTED",
            executable_backend=None,
            reproducibility="N/A_NOT_EXECUTED",
            open_obligations=[
                "general Gilkey a6 formula not independently rederived in this repository -- external "
                "reference only (Gilkey 1975; Vassilevich 2003), PROPOSED/comparison status",
                "even once a6 is resolved, this branch verifies GENERAL Lichnerowicz/Gilkey formulas on "
                "control manifolds only -- it does NOT certify this project's own candidate D_B for "
                "seit_lang.spectral_action's Tr f(D/Lambda), which has never been shown to satisfy the "
                "full Connes spectral-triple axioms (seit_lang/spectral_action.py's own module docstring)",
            ],
            failure_conditions=[
                "an independently rederived a6 formula fails to match the published Gilkey/Vassilevich "
                "result on a solvable control case (the same style of check already applied to a0/a2/a4)",
            ],
            provenance_source="compiler/protocol/derivation_chainlinks.py (D_A^2 verification frontier)",
            source_document_status="N/A",
        ))

    return reg
