"""Execution engine (Phase 6 of reports/derivation_environment/DERIVATION_ENGINE_SPEC.md section 5).

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
from compiler.derivation.types import EpistemicKind, MathObject, MathType


class InadmissiblePremise(ValueError):
    """Raised when a bound premise's epistemic/verification state does not
    meet the leakage-control discipline this engine reuses from
    compiler/verification/self_audit.py::LEAKAGE_ACTIVE_STATUSES (see
    reports/derivation_environment/DERIVATION_ENGINE_SPEC.md section 9)."""


# Phase 9 (spec section 9): a MathObject may be used as a premise without its
# own provenance chain being checked only when it IS the premise -- a
# definition or an explicitly declared assumption -- never when it is a
# claimed/derived result standing in for one.
ADMISSIBLE_WITHOUT_PROVENANCE = {EpistemicKind.DEFINITION, EpistemicKind.ASSUMPTION}

# A premise produced by a Derivation in one of these states is refused
# outright: FALSIFIED/DERIVATION_FAILED/BLOCKED/RETIRED/SUPERSEDED/UNRESOLVED
# results were never certified, and CONDITIONAL results carry an unresolved
# obligation or free parameter -- "without explicit opt-in" per spec section 9.
LEAKAGE_FORBIDDEN_DERIVATION_STATUSES = {
    DerivationStatus.FALSIFIED, DerivationStatus.DERIVATION_FAILED, DerivationStatus.BLOCKED,
    DerivationStatus.RETIRED, DerivationStatus.SUPERSEDED, DerivationStatus.UNRESOLVED,
    DerivationStatus.CONDITIONAL,
}


class DerivationEngine:
    def __init__(self, theorems: TheoremRegistry, *, registries=None):
        self.theorems = theorems
        self.objects: dict[str, MathObject] = {}
        self.derivations = DerivationRegistry()
        # Optional compiler.ir.registry.MDCLRegistries reference, used only to
        # check the compiler Status of a premise that carries a `registry_ref`
        # into the EXISTING canonical registries (spec section 9). Left
        # unwired (None) is fine for premises that are Derivation outputs or
        # raw definitions/assumptions -- it is only required for a premise
        # that claims to already be a canonical MDCL Object/Transformation.
        self.registries = registries

    def add_object(self, obj: MathObject) -> MathObject:
        self.objects[obj.id] = obj
        return obj

    def _find_producing_derivation(self, obj_id: str) -> Derivation | None:
        for d in self.derivations:
            if d.target_id == obj_id or any(s.output_id == obj_id for s in d.steps):
                return d
        return None

    def _check_admissible_premise(self, obj: MathObject, *, allow_conditional: bool) -> None:
        """Enforces reports/derivation_environment/DERIVATION_ENGINE_SPEC.md section 9: refuse a premise
        whose upstream verification state does not meet the leakage-control
        bar, mirroring compiler/verification/self_audit.py's
        LEAKAGE_ACTIVE_STATUSES rather than reimplementing it. Raises
        InadmissiblePremise instead of silently proceeding."""
        if obj.epistemic_kind in ADMISSIBLE_WITHOUT_PROVENANCE:
            return

        if obj.registry_ref is not None:
            if self.registries is None:
                raise InadmissiblePremise(
                    f"{obj.id}: carries registry_ref='{obj.registry_ref}' into the canonical "
                    f"MDCL registries, but this DerivationEngine was constructed without a "
                    f"`registries` reference to check its Status against"
                )
            from compiler.verification.self_audit import LEAKAGE_ACTIVE_STATUSES
            node = None
            for reg in (self.registries.objects, self.registries.transformations,
                        self.registries.equations):
                if obj.registry_ref in reg:
                    node = reg.get(obj.registry_ref)
                    break
            if node is None:
                raise InadmissiblePremise(
                    f"{obj.id}: registry_ref='{obj.registry_ref}' not found in any canonical registry"
                )
            if node.status not in LEAKAGE_ACTIVE_STATUSES:
                raise InadmissiblePremise(
                    f"{obj.id}: registry_ref='{obj.registry_ref}' has compiler Status "
                    f"{node.status.value}, not in "
                    f"{sorted(s.value for s in LEAKAGE_ACTIVE_STATUSES)} -- refused as a premise"
                )
            return

        producing = self._find_producing_derivation(obj.id)
        if producing is None:
            raise InadmissiblePremise(
                f"{obj.id}: a {obj.epistemic_kind.value} object with neither a registry_ref nor "
                f"a producing Derivation on record -- its admissibility cannot be checked"
            )
        forbidden = LEAKAGE_FORBIDDEN_DERIVATION_STATUSES
        if allow_conditional:
            forbidden = forbidden - {DerivationStatus.CONDITIONAL}
        if producing.status in forbidden:
            raise InadmissiblePremise(
                f"{obj.id}: produced by derivation '{producing.derivation_id}' with status "
                f"{producing.status.value} -- refused as a premise"
            )

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
        dependencies: list | None = None, allow_conditional_premises: bool = False,
    ) -> Derivation:
        """Attempts to derive an object of `target_type` from the bound
        premises. If `theorem_id` is given, only that theorem is tried
        (used when the caller already knows which rule applies -- TEST 1-3).
        Otherwise every registered theorem whose conclusion_type matches
        `target_type` is tried in registration order (the general
        derive(target) search behavior), skipping any id in
        `exclude_theorem_ids` (used by RecoveryEngine to avoid re-trying a
        theorem already known to falsify).

        Before any theorem is tried, every MathObject in `bound` is checked
        for leakage-control admissibility (spec section 9): a FALSIFIED,
        BLOCKED, or otherwise uncertified upstream premise is refused, not
        silently used. The refusal itself is recorded as an honest
        DERIVATION_FAILED Derivation rather than raised as a bare exception
        with no audit trail."""
        try:
            for v in bound.values():
                if isinstance(v, MathObject):
                    self._check_admissible_premise(v, allow_conditional=allow_conditional_premises)
        except InadmissiblePremise as exc:
            d = Derivation(
                derivation_id=derivation_id, target_id=target_type.value,
                inputs=[getattr(v, "id", str(v)) for v in bound.values()],
                dependencies=list(dependencies or []),
                status=DerivationStatus.DERIVATION_FAILED,
                note=f"inadmissible premise (leakage-control, spec section 9): {exc}",
            )
            self.derivations.add(d)
            return d

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
