"""Provenance record for the D_A^2=-(nabla^2+E) / Seeley-DeWitt a0,a2,a4,a6
verification pass -- same convention as fc005_reconciliation.py and
continuum_exponent_correction.py: the narrative is recorded as plain data
here, then registered as real Objects in compiler/ir/seeley_dewitt_verification.py.

Requested explicitly: this needed its own independent calculation rather
than being marked verified because surrounding architecture (the discrete/
spectral substrate, GR geometry, Clifford/vierbein self-consistency) was
already verified. D_A^2=-(nabla^2+E) -> a0 -> a2 -> a4 -> a6 -> Tr f(D_A/
Lambda) -> S_eff is a genuinely separate mathematical chain from those
earlier checks and was not covered by them.

SCOPE (repeated from compiler/backends/lichnerowicz_seeley_dewitt.py --
load-bearing, do not drop when this record is read elsewhere): this
verifies the GENERAL Lichnerowicz/Gilkey formulas on standard CONTROL
manifolds (flat 2D for the gauge term, round S^2/S^3 for the gravity
term and Seeley-DeWitt numerics) -- the same status as the existing S^3
heat-kernel control. It does NOT certify this project's own candidate
Dirac operator D_B (seit_lang/incidence_clifford.py,
seit_lang/spectral_action.py) or attach any physical interpretation to
that construction's Tr f(D/Lambda); spectral_action.py's own module
docstring already states D_B has never been shown to satisfy the full
spectral-triple axioms, and nothing here changes that.
"""
from __future__ import annotations

METHOD_SUMMARY = (
    "Two independent symbolic checks isolate the two pieces of E cleanly (neither can mask an "
    "error in the other): (1) GAUGE term via flat 2D Euclidean space with a U(1) gauge field only "
    "(R=0 identically), genuine symbolic operator composition, not textbook quotation; (2) GRAVITY "
    "term via the round unit S^2 with no gauge field, spin connection derived from the Cartan "
    "structure equation, Christoffel symbols computed from the metric, Riemann tensor reusing the "
    "exact sign convention already validated against the textbook FRW Friedmann equations and the "
    "contracted Bianchi identity in an earlier verification pass, Lichnerowicz coefficient SOLVED "
    "FOR rather than assumed to be 1/4. Followed by a numeric Seeley-DeWitt a0/a2/a4 E-dependence "
    "check reusing this project's own already-verified S^3 heat-trace-fit machinery, extended to a "
    "shifted operator (constant E) so the 60*E*R and 180*E^2 terms of Gilkey's a4 -- never "
    "previously exercised in this project (existing S3 control used E=0 only) -- are actually probed."
)

ERRORS_FOUND_AND_FIXED = [
    {
        "stage": "gauge term (flat 2D)",
        "error": "First attempt used bare D_A = gamma^a(d_a+iA_a) (no overall i). Residual came out "
                 "EXACTLY 2x the nabla^2 term instead of zero.",
        "diagnosis": "Bare gamma^a d_a is anti-self-adjoint; D_A^2 then equals +(nabla^2+E) instead "
                     "of -(nabla^2+E) -- comparing it against -(nabla^2+E) doubles the nabla^2 term "
                     "in the residual. Diagnosed by testing the A=0 sub-case first (isolated to "
                     "exactly coefficient +1, not +2, ruling out a Clifford-algebra bug) and then "
                     "reasoning about which sign convention makes D_A self-adjoint.",
        "fix": "D_A = i*gamma^a(d_a+iA_a). Residual became exactly zero on rerun.",
    },
    {
        "stage": "gravity term (round S^2)",
        "error": "First run solved for c in E=c*R*Identity (D^2=-(nabla^2+E)) and got c=-1/4; the "
                 "script's assertion expected c=+1/4 and failed.",
        "diagnosis": "Convention bug in the ASSERTION, not the computation: D^2=-(nabla^2+E) means "
                     "D^2=-nabla^2-E; the textbook Lichnerowicz formula D^2=-nabla^2+R/4 (a PLUS "
                     "sign) is reproduced by -E=R/4, i.e. E=-R/4, i.e. c=-1/4 -- exactly what was "
                     "computed. Re-derived the expected value by hand from the two forms before "
                     "fixing the assertion (not just changing the sign to make it pass).",
        "fix": "Assertion corrected to expect c=-1/4; rerun confirmed E=-R/4*Identity, i.e. "
               "D^2=-nabla^2+R/4, the textbook Lichnerowicz formula, exactly.",
    },
    {
        "stage": "gravity term (Riemann tensor helper, first draft)",
        "error": "An initial from-scratch Riemann tensor formula gave R=-2 for the unit S^2 instead "
                 "of the correct R=+2.",
        "diagnosis": "The derivative-term index order in the from-scratch formula was inconsistent "
                     "with its own curvature (Gamma-Gamma) term -- not simply an overall sign flip.",
        "fix": "Discarded the from-scratch formula and reused the EXACT Riemann-tensor convention "
               "already validated in an earlier session (verify_geometry.py: matched the textbook "
               "FRW Friedmann equations and satisfied the contracted Bianchi identity nabla^mu "
               "G_mu_nu=0 identically). R=2 confirmed on rerun.",
    },
    {
        "stage": "Seeley-DeWitt a0/a2/a4 numeric fit",
        "error": "Degree-3 polynomial fit (the existing S3 control's default) gave a2 relative "
                 "residual 2.52e-4 at E=2.5, just above the 1e-4 tolerance -- all other (E, "
                 "coefficient) combinations passed.",
        "diagnosis": "Confirmed (not assumed) as a fit-window truncation bias, the same effect the "
                     "existing S3-control module's own docstring documents for degree-2 fits at "
                     "E=0: swept the fit degree and found rapid, monotonic convergence to the "
                     "predicted value (2.52e-4 at degree 3, 1.79e-6 at degree 4, 1.24e-8 at degree "
                     "5) -- a converging sequence, not a plateau at a wrong answer, which is the "
                     "signature of a fit-window artifact rather than a formula error.",
        "fix": "fit_degree default raised from 3 to 4; all 4 tested E values pass comfortably "
               "(residuals 1e-7 to 1e-13) at degree 4.",
    },
]

A6_SCOPE_NOTE = (
    "The general Gilkey a6 formula (position-dependent E(x), nonabelian gauge curvature "
    "Omega_{mu nu}, Delta E, and a dozen-plus pure-curvature invariants) was NOT independently "
    "rederived here: reproducing a formula that long from memory, with no primary source available "
    "in this session to cross-check it against, would itself be exactly the kind of unverified "
    "claim this project's own discipline forbids. A narrow, elementary, non-Gilkey-formula-"
    "dependent consistency check was run instead -- for CONSTANT E, Y_E(t)=exp(t*E)*Y_0(t) is a "
    "trivial algebraic identity requiring no heat-kernel theory at all -- and confirmed the fit "
    "machinery is self-consistent through O(t^3) (residuals ~1e-4 to 1e-6 at 3 nonzero E values). "
    "This does NOT verify the general a6 formula for non-constant E(x) or nonzero gauge curvature. "
    "External reference only, PROPOSED/comparison status: Gilkey, P.B. (1975), 'The spectral "
    "geometry of the second order elliptic differential operator'; Vassilevich, D.V. (2003), "
    "'Heat kernel expansion: user's manual', Phys. Rept. 388."
)
