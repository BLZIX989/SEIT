"""Certification mapping (Phase 13 of the implementation plan). The ONE
integration point between the new, additive DerivationStatus and the
existing compiler.core.status.Status (reports/derivation_environment/DERIVATION_ENGINE_SPEC.md section 6).
A pure function (`to_canonical_status`) plus the actual registration call
into the EXISTING registries/provenance machinery
(compiler.ir.registry.MDCLRegistries, compiler.provenance.provenance.
make_provenance) -- neither is reimplemented here.

The mapping is one-directional (Derivation -> Status, never the reverse) and
applied ONLY at the moment a Derivation reaches CANONICAL: every
Derivation-layer-only state (DOCUMENTED, FORMALIZED, DERIVABLE, DERIVED
before EXECUTED, EXECUTED before VERIFIED, SUPERSEDED, RETIRED) is never
registered into the canonical registries at all.
"""
from __future__ import annotations

from compiler.core.ir import Object
from compiler.core.status import Status
from compiler.derivation.derivation import Derivation, DerivationStatus
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

# DerivationStatus -> Status, exactly the table in reports/derivation_environment/DERIVATION_ENGINE_SPEC.md
# section 6. Anything absent from this dict maps to None: "never registered
# into the canonical registries at all" (pre-canonical or historical
# Derivation-layer-only states).
_STATUS_TABLE = {
    DerivationStatus.CONDITIONAL: Status.CONDITIONAL,
    DerivationStatus.DERIVATION_FAILED: Status.OPEN,
    DerivationStatus.BLOCKED: Status.OPEN,
    DerivationStatus.UNRESOLVED: Status.OPEN,
    DerivationStatus.FALSIFIED: Status.FALSIFIED,
}


def to_canonical_status(d: Derivation, *, single_evidence_tier: bool = False) -> Status | None:
    """CANONICAL maps to VERIFIED when the Derivation's own record shows
    more than one independent evidence tier (Phase 7's numeric+symbolic
    cross-checks both SATISFIED), or to CALCULATED when the caller declares
    (via `single_evidence_tier`) that only one evidence tier was actually
    run -- mirroring the existing DERIVED-vs-CALCULATED distinction already
    documented in compiler/core/status.py, not a new convention."""
    if d.status == DerivationStatus.CANONICAL:
        return Status.CALCULATED if single_evidence_tier else Status.VERIFIED
    return _STATUS_TABLE.get(d.status)


def register_canonical_derivation(
    d: Derivation, registries: MDCLRegistries, *,
    single_evidence_tier: bool = False, source: str = "compiler/derivation",
) -> Object | None:
    """Registers a Derivation into the EXISTING MDCL registries as an
    Object, cross-referenced back to its Derivation record via
    provenance.calculation_id. Returns the registered Object, or None if `d`
    is not (yet) VERIFIED or CANONICAL -- every other DerivationStatus is
    refused, and nothing is registered.

    Per DerivationStatus's own docstring ("CANONICAL = VERIFIED + registered
    into the existing MDCL registries"), THIS function is the one place that
    promotion happens: a VERIFIED `d` is promoted to CANONICAL as part of
    registering it (idempotent if `d` already reached CANONICAL some other
    way, e.g. RecoveryEngine's own successful-recovery promotion).

    Never re-derives or duplicates the mathematical content: the
    registered Object's carrier is None, and the real numeric/symbolic
    evidence stays in derivation_registry.json, the same identity/
    calculation split this project's Object/Provenance model already uses
    everywhere else."""
    if d.status not in (DerivationStatus.VERIFIED, DerivationStatus.CANONICAL):
        return None
    d.status = DerivationStatus.CANONICAL
    status = to_canonical_status(d, single_evidence_tier=single_evidence_tier)
    assert status is not None  # CANONICAL always maps to a concrete Status

    obj_id = f"DERIV::{d.derivation_id}"
    if obj_id in registries.objects:
        return registries.objects.get(obj_id)

    obj = Object(
        id=obj_id, type="derivation_result", status=status,
        dependencies=list(d.dependencies), role="upstream_construction",
    )
    n_satisfied = sum(1 for o in d.proof_obligations if o.result.value == "SATISFIED")
    obj.provenance = make_provenance(
        source=source, object_id=obj.id, calculation_id=d.derivation_id,
        status=status, dependency_ids=list(d.dependencies),
        verification={
            "derivation_status": d.status.value,
            "n_proof_obligations": len(d.proof_obligations),
            "n_satisfied": n_satisfied,
        },
    )
    registries.objects.add_object(obj)
    d.provenance.setdefault("registered_object_id", obj.id)
    return obj
