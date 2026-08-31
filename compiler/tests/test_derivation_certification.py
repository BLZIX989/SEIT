"""Phase 13: certification mapping (compiler/derivation/certification.py).
Runs a Slice-1 derivation through to registration into the EXISTING
compiler.ir.registry.MDCLRegistries and confirms the resulting
status_matrix entry carries the DerivationStatus-mapped compiler Status,
cross-referenced back to the Derivation via provenance.calculation_id --
DERIVATION_ENGINE_SPEC.md section 6's one-directional integration point.
"""
from __future__ import annotations

from compiler.backends.graph_laplacian import build_graph
from compiler.core.status import Status
from compiler.derivation.builtin_theorems import build_default_theorem_registry
from compiler.derivation.certification import register_canonical_derivation, to_canonical_status
from compiler.derivation.derivation import Derivation, DerivationStatus
from compiler.derivation.engine import DerivationEngine
from compiler.derivation.types import EpistemicKind, MathObject, MathType
from compiler.ir.registry import MDCLRegistries


def test_to_canonical_status_table():
    def _mk(status):
        return Derivation(derivation_id="X", target_id="Y", status=status)

    assert to_canonical_status(_mk(DerivationStatus.CANONICAL)) == Status.VERIFIED
    assert to_canonical_status(_mk(DerivationStatus.CANONICAL), single_evidence_tier=True) == Status.CALCULATED
    assert to_canonical_status(_mk(DerivationStatus.CONDITIONAL)) == Status.CONDITIONAL
    assert to_canonical_status(_mk(DerivationStatus.DERIVATION_FAILED)) == Status.OPEN
    assert to_canonical_status(_mk(DerivationStatus.BLOCKED)) == Status.OPEN
    assert to_canonical_status(_mk(DerivationStatus.UNRESOLVED)) == Status.OPEN
    assert to_canonical_status(_mk(DerivationStatus.FALSIFIED)) == Status.FALSIFIED
    # pre-canonical / historical Derivation-layer-only states: never registered
    for s in (DerivationStatus.DOCUMENTED, DerivationStatus.FORMALIZED, DerivationStatus.DERIVABLE,
              DerivationStatus.DERIVED, DerivationStatus.EXECUTED, DerivationStatus.VERIFIED,
              DerivationStatus.SUPERSEDED, DerivationStatus.RETIRED):
        assert to_canonical_status(_mk(s)) is None


def test_verified_slice1_derivation_registers_as_canonical(tmp_path):
    engine = DerivationEngine(build_default_theorem_registry())
    g = build_graph("cycle", 6)
    graph_obj = engine.add_object(MathObject(
        id="G-cert", math_type=MathType.GRAPH, epistemic_kind=EpistemicKind.DEFINITION, carrier=g,
    ))
    d = engine.derive("D-CERT", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                       theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD")
    assert d.status == DerivationStatus.VERIFIED

    registries = MDCLRegistries()
    obj = register_canonical_derivation(d, registries)

    assert obj is not None
    assert d.status == DerivationStatus.CANONICAL  # promoted by registration itself
    assert obj.status == Status.VERIFIED
    assert obj.provenance.calculation_id == "D-CERT"
    assert d.provenance["registered_object_id"] == obj.id

    rows = registries.status_matrix()
    row = next(r for r in rows if r["id"] == obj.id)
    assert row["status"] == "VERIFIED"

    out_dir = tmp_path / "mdcl"
    registries.dump_all(out_dir)
    import json
    status_matrix = json.loads((out_dir / "status_matrix.json").read_text())
    assert any(r["id"] == obj.id and r["status"] == "VERIFIED" for r in status_matrix)


def test_falsified_derivation_never_registers_as_canonical():
    d = Derivation(derivation_id="D-BAD", target_id="Y", status=DerivationStatus.FALSIFIED)
    registries = MDCLRegistries()
    obj = register_canonical_derivation(d, registries)
    assert obj is None
    assert d.status == DerivationStatus.FALSIFIED  # untouched
    assert len(registries.objects) == 0


def test_registration_is_idempotent():
    engine = DerivationEngine(build_default_theorem_registry())
    g = build_graph("path", 4)
    graph_obj = engine.add_object(MathObject(
        id="G-idem", math_type=MathType.GRAPH, epistemic_kind=EpistemicKind.DEFINITION, carrier=g,
    ))
    d = engine.derive("D-IDEM", MathType.POSITIVE_SEMIDEFINITE_OPERATOR, {"graph": graph_obj},
                       theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD")
    registries = MDCLRegistries()
    obj1 = register_canonical_derivation(d, registries)
    obj2 = register_canonical_derivation(d, registries)
    assert obj1.id == obj2.id
    assert len(registries.objects) == 1
