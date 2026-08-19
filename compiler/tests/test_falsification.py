from compiler.falsification.protocols import (
    mathematical_invariance_test, representation_invariance_test,
    structural_elimination_protocol,
)
from compiler.falsification.target_independence import scan_node


def test_structural_elimination_falsifies_non_unique_target():
    candidates = [1, 2, 3, 4]  # multiple integers satisfy "is even"
    rec = structural_elimination_protocol(
        record_id="SE-1", target="the-even-number",
        candidates=candidates, predicate=lambda x: x % 2 == 0,
    )
    assert not rec.passed  # 2 and 4 both survive -> not unique


def test_structural_elimination_passes_for_unique_target():
    candidates = [1, 2, 3, 4]
    rec = structural_elimination_protocol(
        record_id="SE-2", target="the-number-greater-than-3",
        candidates=candidates, predicate=lambda x: x > 3,
    )
    assert rec.passed  # only 4 survives


def test_representation_invariance_detects_dependence():
    # invariant_fn depends on list order -> representation-dependent
    reps = [[1, 2, 3], [3, 2, 1]]
    rec = representation_invariance_test(
        record_id="RI-1", target="first-element",
        representations=reps, invariant_fn=lambda r: r[0],
    )
    assert not rec.passed


def test_representation_invariance_passes_for_true_invariant():
    reps = [[1, 2, 3], [3, 2, 1]]
    rec = representation_invariance_test(
        record_id="RI-2", target="sum",
        representations=reps, invariant_fn=lambda r: sum(r),
    )
    assert rec.passed


def test_mathematical_invariance_detects_broken_invariant():
    rec = mathematical_invariance_test(
        record_id="MI-1", target="first-element-under-relabeling",
        transformations=[lambda r: list(reversed(r))],
        base_object=[1, 2, 3],
        invariant_fn=lambda r: r[0],
    )
    assert not rec.passed


def test_target_independence_scan_flags_forbidden_term_in_upstream_role():
    findings = scan_node("N1", ["gauge group is SU(3) x SU(2) x U(1)"], role="upstream_construction")
    assert findings
    assert all(not f.allowed for f in findings)


def test_target_independence_scan_allows_forbidden_term_in_validation_role():
    findings = scan_node("N2", ["compare prediction to observed CKM matrix"], role="validation")
    assert findings
    assert all(f.allowed for f in findings)
