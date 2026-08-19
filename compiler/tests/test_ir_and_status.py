from compiler.core.ir import Equation, Object, Transformation
from compiler.core.status import Status, can_transition, map_legacy_status


def test_object_default_role_is_upstream_construction():
    o = Object(id="O1", type="graph")
    assert o.role == "upstream_construction"


def test_status_transition_open_to_calculated_allowed():
    assert can_transition(Status.OPEN, Status.CALCULATED)


def test_status_transition_verified_to_open_forbidden():
    assert not can_transition(Status.VERIFIED, Status.OPEN)


def test_falsified_is_terminal():
    assert can_transition(Status.FALSIFIED, Status.FALSIFIED)
    assert not can_transition(Status.FALSIFIED, Status.VERIFIED)


def test_ir_node_set_status_raises_on_illegal_transition():
    o = Object(id="O2", type="graph", status=Status.VERIFIED)
    try:
        o.set_status(Status.OPEN)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_legacy_prose_claims_never_promoted_above_proposed():
    # A document claiming "CERTIFIED" or "DERIVED" must not be taken at
    # face value (spec section 2) -- it always maps to PROPOSED.
    for label in ("CERTIFIED", "DERIVED", "VERIFIED", "PROVEN", "SOLVED"):
        assert map_legacy_status(label) == Status.PROPOSED


def test_equation_to_dict_serializes_status_as_string():
    eq = Equation(id="E1", lhs="L", rhs="D - A", status=Status.CALCULATED)
    d = eq.to_dict()
    assert d["status"] == "CALCULATED"


def test_transformation_defaults():
    t = Transformation(id="T1", domain="Graph", codomain="Operator")
    assert t.status == Status.OPEN
    assert t.dependencies == []
