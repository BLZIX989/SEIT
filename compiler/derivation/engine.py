"""Execution engine (Phase 6 of DERIVATION_ENGINE_SPEC.md section 5).

Deliberately thin orchestration: DerivationEngine never reimplements numeric
or symbolic mathematics itself -- every Theorem's `transformation` calls into
an existing compiler/backends/* function or a small, honest new check. The
engine's job is target resolution, candidate search, obligation-driven status
computation, and Derivation-trace bookkeeping.
"""
from __future__ import annotations

from compiler.derivation.derivation import (
    Derivation, DerivationRegistry, DerivationStatus, DerivationStep,
)
from compiler.derivation.obligations import ObligationResult
from compiler.derivation.theorems import TheoremNotImplemented, TheoremRegistry
from compiler.derivation.types import MathObject, MathType


class InadmissiblePremise(ValueError):
    """Raised when a bound premise's epistemic/verification state does not
    meet the leakage-control discipline this engine reuses from
    compiler/verification/self_audit.py::LEAKAGE_ACTIVE_STATUSES (see
    DERIVATION_ENGINE_SPEC.md section 9)."""


class DerivationEngine:
    def __init__(self, theorems: TheoremRegistry):
        self.theorems = theorems
        self.objects: dict[str, MathObject] = {}
        self.derivations = DerivationRegistry()

    def add_object(self, obj: MathObject) -> MathObject:
        self.objects[obj.id] = obj
        return obj

    @staticmethod
    def _status_from_obligations(obligations) -> DerivationStatus:
        if any(o.result == ObligationResult.FAILED for o in obligations):
            return DerivationStatus.FALSIFIED
        if any(o.result == ObligationResult.NOT_TESTED for o in obligations):
            return DerivationStatus.CONDITIONAL
        if obligations and all(o.result == ObligationResult.SATISFIED for o in obligations):
            return DerivationStatus.VERIFIED
        return DerivationStatus.DERIVATION_FAILED

    def derive(
        self, derivation_id: str, target_type: MathType, bound: dict,
        *, theorem_id: str | None = None, exclude_theorem_ids: frozenset = frozenset(),
        dependencies: list | None = None,
    ) -> Derivation:
        """Attempts to derive an object of `target_type` from the bound
        premises. If `theorem_id` is given, only that theorem is tried
        (used when the caller already knows which rule applies -- TEST 1-3).
        Otherwise every registered theorem whose conclusion_type matches
        `target_type` is tried in registration order (the general
        derive(target) search behavior), skipping any id in
        `exclude_theorem_ids` (used by RecoveryEngine to avoid re-trying a
        theorem already known to falsify)."""
        if theorem_id is not None:
            candidates = [self.theorems.get(theorem_id)]
        else:
            candidates = [
                t for t in self.theorems.candidates_for(target_type)
                if t.theorem_id not in exclude_theorem_ids
            ]

        rejected: list[tuple] = []
        for th in candidates:
            try:
                applicable = th.check_applicable(bound)
            except TheoremNotImplemented as exc:
                rejected.append((th.theorem_id, f"not implemented: {exc}"))
                continue
            if not applicable:
                rejected.append((th.theorem_id, "applicability_check returned False"))
                continue

            try:
                output, obligations = th.apply(bound)
            except TheoremNotImplemented as exc:
                rejected.append((th.theorem_id, f"not implemented: {exc}"))
                continue
            except Exception as exc:  # a raising transformation is a real derivation failure
                d = Derivation(
                    derivation_id=derivation_id, target_id=target_type.value,
                    inputs=[getattr(v, "id", str(v)) for v in bound.values()],
                    dependencies=list(dependencies or []),
                    status=DerivationStatus.DERIVATION_FAILED,
                    note=f"{th.theorem_id} raised {type(exc).__name__} during apply(): {exc}",
                    provenance={"theorem": th.theorem_id},
                )
                self.derivations.add(d)
                return d

            self.add_object(output)
            status = self._status_from_obligations(obligations)
            step = DerivationStep(
                step_id=f"{derivation_id}-step1", rule_id=th.theorem_id,
                input_ids=[getattr(v, "id", str(v)) for v in bound.values()],
                output_id=output.id, symbolic_form=th.conclusion,
            )
            d = Derivation(
                derivation_id=derivation_id, target_id=output.id,
                inputs=[getattr(v, "id", str(v)) for v in bound.values()],
                steps=[step], proof_obligations=obligations,
                dependencies=list(dependencies or []), status=status,
                provenance={"theorem": th.theorem_id, "domain": th.domain, "source": th.provenance},
            )
            self.derivations.add(d)
            return d

        d = Derivation(
            derivation_id=derivation_id, target_id=target_type.value,
            inputs=[getattr(v, "id", str(v)) for v in bound.values()],
            dependencies=list(dependencies or []),
            status=DerivationStatus.DERIVATION_FAILED,
            note=f"no applicable, implemented theorem found for {target_type.value}; "
                 f"rejected candidates: {rejected}",
        )
        self.derivations.add(d)
        return d
