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

    return reg
