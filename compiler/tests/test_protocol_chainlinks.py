"""Phase 12: tests for the Chainlink/Protocol projection layer
(compiler/protocol/). These build the real MDCL once (via
compiler.run_compiler.build_and_run's own registration path, replicated
here directly rather than importing the module-level run to keep this
test isolated from filesystem writes) and assert the chainlink layer
never claims anything stronger than the real registries it wraps.
"""
from __future__ import annotations

from compiler.core.status import Status
from compiler.falsification.protocols import (
    FalsificationRecord, representation_invariance_test,
)
from compiler.ir.executable_tests import register_executable_tests
from compiler.ir.registry import MDCLRegistries
from compiler.protocol.build_protocols import build_protocol_registry
from compiler.protocol.derivation_chainlinks import (
    _REAL_CHAINLINKS, build_derivation_chainlinks,
)


def _build():
    registries = MDCLRegistries()
    test_results = register_executable_tests(registries)
    falsifications: list[FalsificationRecord] = list(test_results["falsifications"])
    # a real (trivially-passing) representation-invariance record targeting
    # Spec(L), same as run_compiler.py adds -- included so
    # CL-L-TO-SPECL's falsification_status test below is meaningful.
    falsifications.append(representation_invariance_test(
        record_id="FALS-SPECTRUM-RELABELING-INVARIANCE", target="Spec(L) test",
        representations=[1, 1, 1], invariant_fn=lambda x: x,
    ))
    return registries, falsifications


def test_chainlink_status_never_exceeds_the_real_transformation_it_wraps():
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    for chainlink_id, transformation_id, _ in _REAL_CHAINLINKS:
        link = chainlinks.get(chainlink_id)
        t = registries.transformations.get(transformation_id)
        real_status = t.status.value if isinstance(t.status, Status) else t.status
        assert link.status == real_status, (
            f"{chainlink_id} claims status {link.status} but the real transformation "
            f"{transformation_id} is {real_status}"
        )
        assert link.calculation_status == real_status


def test_chainlink_dependencies_match_the_real_transformation():
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    for chainlink_id, transformation_id, _ in _REAL_CHAINLINKS:
        link = chainlinks.get(chainlink_id)
        t = registries.transformations.get(transformation_id)
        assert link.dependencies == list(t.dependencies)


def test_frontier_chainlink_is_open_with_explicit_obstruction():
    """The METRIC-CANDIDATE -> CONNECTION-NODE chainlink is the real,
    honest frontier this build's executed chain stops at (Phase 12 first
    execution task) -- it must never silently claim a stronger status,
    and must document exactly why it is blocked."""
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    frontier = chainlinks.get("CL-METRIC-TO-CONNECTION")
    assert frontier.status == "OPEN"
    assert frontier.proof_status == "OPEN"
    assert frontier.executable_backend is None
    assert frontier.reproducibility == "N/A_NOT_EXECUTED"
    assert len(frontier.open_obligations) > 0


def test_falsification_status_reflects_real_non_uniqueness_finding():
    """Test 2's own backend classifies the diffusion-distance metric
    candidate as non-unique (never 'exact') -- the chainlink wrapping
    DIFFUSION-DISTANCE -> METRIC-CANDIDATE must surface that real failure,
    not paper over it."""
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    link = chainlinks.get("CL-DIFFUSION-TO-METRIC")
    assert link.falsification_status == "TESTED_FAILED"


def test_falsification_status_reflects_real_survived_invariance_test():
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    link = chainlinks.get("CL-L-TO-SPECL")
    assert link.falsification_status == "TESTED_SURVIVED"


def test_untested_chainlinks_are_honestly_not_tested():
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    for chainlink_id in ("CL-G-TO-L", "CL-SPECL-TO-HEATFLOW", "CL-HEATFLOW-TO-KERNEL",
                          "CL-SPECL-TO-DIFFUSION"):
        assert chainlinks.get(chainlink_id).falsification_status == "NOT_TESTED"


def test_chainlink_registry_rejects_duplicate_ids():
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    dup = chainlinks.get("CL-G-TO-L")
    try:
        chainlinks.add(dup)
        assert False, "expected ValueError on duplicate chainlink id"
    except ValueError:
        pass


def test_chainlink_to_dict_shape_is_json_serializable():
    import json
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    payload = json.dumps(chainlinks.to_list())
    assert "CL-G-TO-L" in payload
    assert "CL-METRIC-TO-CONNECTION" in payload


def test_protocol_registry_wraps_exactly_the_real_chainlinks():
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    protocols = build_protocol_registry(chainlinks)
    graph_protocol = protocols.get("PROTOCOL-GRAPH-SPECTRAL-DERIVATION")
    assert set(graph_protocol.chainlinks) == set(chainlinks.ids())


def test_falsification_protocol_source_document_status_is_honest():
    """The historical SEP/RIT/MIT/OISR specification text is not present
    in this repository (see compiler/protocol/__init__.py) -- the protocol
    record must say so explicitly rather than implying recovery."""
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    protocols = build_protocol_registry(chainlinks)
    falsification_protocol = protocols.get("PROTOCOL-STRUCTURAL-FALSIFICATION")
    assert falsification_protocol.source_document_status == "MISSING_SOURCE"


def test_no_chainlink_status_is_ever_falsified_or_verified_without_backend_agreement():
    """Cross-check every chainlink's proof_status is only ever a
    'proven'-flavored value when the underlying transformation actually
    reached an admissible status -- catches the failure mode of a
    chainlink asserting proof strength independent of real execution."""
    registries, falsifications = _build()
    chainlinks = build_derivation_chainlinks(registries, falsifications)
    admissible = {"VERIFIED", "DERIVED", "CALCULATED", "CONDITIONAL"}
    for link in chainlinks:
        if link.proof_status == "PROVEN_DEFINITIONAL":
            assert link.status in admissible, (
                f"{link.chainlink_id} claims PROVEN_DEFINITIONAL but status is {link.status}"
            )
