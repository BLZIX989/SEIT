"""TEST 1, TEST 2, TEST 3 from the Universal Mathematical Derivation
Environment task (section 20): G -> L, L -> Spec(L), L -> e^{-tL}, executed
through the new compiler/derivation/ engine rather than calling the backend
functions directly -- proving the engine's type checking, obligation
discharge, and status computation actually work end to end."""
from __future__ import annotations

import numpy as np

from compiler.backends.graph_laplacian import build_graph
from compiler.derivation.builtin_theorems import build_default_theorem_registry
from compiler.derivation.derivation import DerivationStatus
from compiler.derivation.engine import DerivationEngine
from compiler.derivation.obligations import ObligationResult
from compiler.derivation.types import EpistemicKind, MathObject, MathType, require
from compiler.derivation.types import TypeCompositionError


def _make_engine():
    return DerivationEngine(build_default_theorem_registry())


def test_test1_graph_to_laplacian_symmetric_psd():
    engine = _make_engine()
    g = build_graph("cycle", 6)
    graph_obj = engine.add_object(MathObject(
        id="G-cycle6", math_type=MathType.GRAPH, epistemic_kind=EpistemicKind.DEFINITION, carrier=g,
    ))

    d = engine.derive("D-TEST1", MathType.POSITIVE_SEMIDEFINITE_OPERATOR,
                       {"graph": graph_obj}, theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD")

    assert d.status == DerivationStatus.VERIFIED
    assert len(d.steps) == 1
    assert d.steps[0].rule_id == "THM-SYMMETRIC-QUADRATIC-FORM-PSD"
    assert all(o.result == ObligationResult.SATISFIED for o in d.proof_obligations)
    obligation_ids = {o.obligation_id for o in d.proof_obligations}
    assert {"symmetric-numeric", "symmetric-symbolic", "positive-semidefinite"} <= obligation_ids

    L_obj = engine.objects[d.steps[0].output_id]
    assert L_obj.math_type == MathType.POSITIVE_SEMIDEFINITE_OPERATOR
    assert L_obj.verified_properties["symmetric"] is True
    assert L_obj.verified_properties["positive_semidefinite"] is True
    # type system enforcement: a bare, unchecked matrix must NOT satisfy `require`
    raw = MathObject(id="raw", math_type=MathType.MATRIX, epistemic_kind=EpistemicKind.DEFINITION,
                      carrier=np.zeros((3, 3)))
    try:
        require(raw, MathType.SELF_ADJOINT_OPERATOR)
        assert False, "require() should have rejected an unchecked bare Matrix"
    except TypeCompositionError:
        pass
    return engine, L_obj


def test_test2_laplacian_to_spectrum():
    engine, L_obj = test_test1_graph_to_laplacian_symmetric_psd()

    d = engine.derive("D-TEST2", MathType.SPECTRUM, {"operator": L_obj},
                       theorem_id="THM-SPECTRAL-DECOMPOSITION-REAL-SYMMETRIC")

    assert d.status == DerivationStatus.VERIFIED
    spec_obj = engine.objects[d.steps[0].output_id]
    assert spec_obj.math_type == MathType.SPECTRUM
    assert spec_obj.verified_properties["eigendecomposition_valid"] is True
    # cross-check the derivation engine's result against the backend called directly
    from compiler.backends.spectral import spectrum
    direct = spectrum(L_obj.carrier)
    assert np.allclose(sorted(spec_obj.carrier.eigenvalues), sorted(direct.eigenvalues))
    return engine, L_obj, spec_obj


def test_test3_laplacian_to_heat_kernel():
    engine, L_obj, spec_obj = test_test2_laplacian_to_spectrum()

    d = engine.derive("D-TEST3", MathType.HEAT_KERNEL,
                       {"operator": L_obj, "spectrum": spec_obj, "t": 0.5},
                       theorem_id="THM-MATRIX-EXPONENTIAL-SEMIGROUP")

    assert d.status == DerivationStatus.VERIFIED
    H_obj = engine.objects[d.steps[0].output_id]
    assert H_obj.math_type == MathType.HEAT_KERNEL
    assert H_obj.verified_properties["semigroup"] is True
    obligation_ids = {o.obligation_id for o in d.proof_obligations}
    assert {"heat-kernel-identity-at-zero", "heat-kernel-semigroup"} <= obligation_ids


def test_derivation_registry_round_trips_to_json(tmp_path):
    engine = _make_engine()
    g = build_graph("path", 5)
    graph_obj = engine.add_object(MathObject(
        id="G-path5", math_type=MathType.GRAPH, epistemic_kind=EpistemicKind.DEFINITION, carrier=g,
    ))
    engine.derive("D-ROUNDTRIP", MathType.POSITIVE_SEMIDEFINITE_OPERATOR,
                  {"graph": graph_obj}, theorem_id="THM-SYMMETRIC-QUADRATIC-FORM-PSD")
    out = tmp_path / "derivation_registry.json"
    engine.derivations.dump_json(out)
    import json
    data = json.loads(out.read_text())
    assert len(data) == 1
    assert data[0]["derivation_id"] == "D-ROUNDTRIP"
    assert data[0]["status"] == "VERIFIED"


def test_unimplemented_theorem_is_refused_not_silently_skipped():
    engine = _make_engine()
    d = engine.derive("D-UNIMPL", MathType.CONNECTION, {}, theorem_id=None)
    assert d.status == DerivationStatus.DERIVATION_FAILED
    assert "THM-LEVI-CIVITA-UNIQUENESS" in d.note
    assert "not implemented" in d.note
