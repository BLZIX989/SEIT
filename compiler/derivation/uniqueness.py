"""Uniqueness engine (Phase 12 of the implementation plan). Runs every
implemented, applicable theorem for `target_type` against bound premises,
collects EVERY candidate whose obligations are all SATISFIED, and reports
only the SEARCH-RESULT CARDINALITY -- never inferring "singleton" from "only
one candidate was tried and it worked."

This is the literal fix for the project's own GEO-001 finding
(compiler/falsification/eigen_uniqueness.py::run_counterexample, wired into
compiler/ir/fc005.py as SPEC-H-UNIQUENESS, and registered there as OPEN, not
CERTIFIED): Spec(H) does not determine H, so any engine that claimed
"singleton" purely because its own search happened to try only one candidate
would repeat exactly the mistake that counterexample falsifies. Task section
15 is explicit that "singleton" requires an actual uniqueness ARGUMENT, not
merely an unexhausted search.
"""
from __future__ import annotations

from typing import Literal

from compiler.derivation.engine import DerivationEngine
from compiler.derivation.equivalence import EquivalenceEngine
from compiler.derivation.obligations import ObligationResult
from compiler.derivation.theorems import TheoremNotImplemented
from compiler.derivation.types import MathType

Cardinality = Literal["empty", "singleton", "finite", "continuous", "unknown"]

# An obligation whose id carries this prefix marks a genuinely free,
# unjustified continuous parameter in an otherwise-satisfied candidate (e.g.
# a free time/scale parameter with no admissibility argument fixing it) --
# see DerivationStatus.CONDITIONAL's own docstring. Its presence caps the
# cardinality finding at "continuous" rather than "singleton"/"finite", even
# when every other obligation for that candidate is SATISFIED.
FREE_PARAMETER_OBLIGATION_PREFIX = "free-parameter:"


class UniquenessEngine:
    def __init__(self, engine: DerivationEngine, equivalence: EquivalenceEngine | None = None):
        self.engine = engine
        self.equivalence = equivalence or EquivalenceEngine()

    def admissible_set(
        self, target_type: MathType, bound: dict, *,
        exclude_theorem_ids: frozenset = frozenset(),
        equivalence_witnesses: dict | None = None,
    ) -> tuple[Cardinality, list]:
        """Returns (classification, satisfying_candidates) where each
        satisfying candidate is (theorem, output_MathObject).

        `equivalence_witnesses`, if given, maps frozenset({theorem_id_a,
        theorem_id_b}) -> a witness dict passed to EquivalenceEngine.classify
        to determine whether two satisfying candidates are the SAME
        admissible construction under a verified equivalence, rather than
        two genuinely distinct ones. Never returns 'singleton' unless
        exactly one candidate satisfied its obligations AND that theorem
        carries `proves_uniqueness=True` (a genuine cited uniqueness
        argument). Never returns 'empty' from an incomplete search -- that
        would claim a nonexistence PROOF this engine does not have;
        'unknown' is the honest default there too."""
        satisfying: list[tuple] = []
        has_free_parameter = False
        for th in self.engine.theorems.candidates_for(target_type):
            if th.theorem_id in exclude_theorem_ids:
                continue
            try:
                if not th.check_applicable(bound):
                    continue
                output, obligations = th.apply(bound)
            except TheoremNotImplemented:
                continue
            except Exception:
                continue

            free_param_obligations = [
                o for o in obligations if o.obligation_id.startswith(FREE_PARAMETER_OBLIGATION_PREFIX)
            ]
            core_obligations = [o for o in obligations if o not in free_param_obligations]
            if not core_obligations or not all(
                o.result == ObligationResult.SATISFIED for o in core_obligations
            ):
                continue
            if free_param_obligations:
                has_free_parameter = True
            satisfying.append((th, output))

        if not satisfying:
            return "unknown", []

        if has_free_parameter:
            return "continuous", satisfying

        if len(satisfying) == 1:
            th, _ = satisfying[0]
            if getattr(th, "proves_uniqueness", False):
                return "singleton", satisfying
            return "unknown", satisfying

        # >= 2 satisfying candidates. An equivalence witness can tell us two
        # candidates are the SAME admissible construction (recorded here for
        # audit), but collapsing to fewer equivalence classes is still not a
        # positive INEQUIVALENCE argument for the remaining ones -- reporting
        # 'finite' would claim we know the exact count of genuinely distinct
        # solutions, which this engine cannot certify without a registered
        # inequivalence proof (not implemented in this phase). This is the
        # direct fix for the project's own GEO-001 finding: two candidates
        # (e.g. H and H'=UHU^dagger from compiler/falsification/
        # eigen_uniqueness.py) both satisfying "has this spectrum" must never
        # be reported as 'singleton' -- 'unknown' is the honest finding here,
        # exactly as this project's own prior audit already established.
        witnesses = equivalence_witnesses or {}
        for (th_a, out_a), (th_b, out_b) in zip(satisfying, satisfying[1:]):
            key = frozenset({th_a.theorem_id, th_b.theorem_id})
            witness = witnesses.get(key)
            if witness:
                self.equivalence.classify(out_a, out_b, witness=witness)  # recorded for audit only
        return "unknown", satisfying
