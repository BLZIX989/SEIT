import pytest

from compiler.core.ir import Object
from compiler.core.status import Status
from compiler.dependencies.graph import (
    CycleError, DependencyError, DependencyGraph, ExecutionGuard,
)
from compiler.ir.registry import MDCLRegistries


def test_topological_order_simple_chain():
    g = DependencyGraph()
    g.add_dependency("B", "A")
    g.add_dependency("C", "B")
    order = g.topological_order()
    assert order.index("A") < order.index("B") < order.index("C")


def test_cycle_rejected():
    g = DependencyGraph()
    g.add_dependency("B", "A")
    g.add_dependency("C", "B")
    with pytest.raises(CycleError):
        g.add_dependency("A", "C")  # A -> C -> B -> A


def test_self_loop_rejected():
    g = DependencyGraph()
    g.add_node("A")
    with pytest.raises(CycleError):
        g.add_dependency("A", "A")


def test_unreachable_nodes_detected():
    g = DependencyGraph()
    g.add_dependency("B", "A")
    g.add_node("ISLAND")
    assert "ISLAND" in g.unreachable_nodes(roots=["A"])
    assert "B" not in g.unreachable_nodes(roots=["A"])


def test_execution_guard_stops_branch_on_open_upstream():
    regs = MDCLRegistries()
    upstream = Object(id="U1", type="Vacuum", status=Status.OPEN)
    downstream = Object(id="D1", type="Distinction", status=Status.OPEN, dependencies=["U1"])
    regs.objects.add_object(upstream)
    regs.objects.add_object(downstream)
    g = DependencyGraph()
    g.add_dependency("D1", "U1")
    guard = ExecutionGuard(g, regs)
    with pytest.raises(DependencyError):
        guard.check("D1")


def test_execution_guard_allows_calculated_upstream():
    regs = MDCLRegistries()
    upstream = Object(id="U2", type="Graph", status=Status.CALCULATED)
    downstream = Object(id="D2", type="Laplacian", status=Status.OPEN, dependencies=["U2"])
    regs.objects.add_object(upstream)
    regs.objects.add_object(downstream)
    g = DependencyGraph()
    g.add_dependency("D2", "U2")
    guard = ExecutionGuard(g, regs)
    guard.check("D2")  # should not raise
