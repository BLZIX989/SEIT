"""Graph construction and Laplacian operator (spec section 13, 31: L = D - A).

Multiple topologies and sizes are supported so downstream claims can be
swept rather than demonstrated on one convenient example (spec 24, 31).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import sympy


@dataclass
class Graph:
    topology: str
    n: int
    seed: int | None
    nodes: list[int]
    edges: list[tuple[int, int]]

    @property
    def label(self) -> str:
        return f"{self.topology}(n={self.n}{f',seed={self.seed}' if self.seed is not None else ''})"

    def adjacency(self) -> np.ndarray:
        A = np.zeros((self.n, self.n), dtype=float)
        for i, j in self.edges:
            A[i, j] = 1.0
            A[j, i] = 1.0
        return A

    def adjacency_exact(self) -> sympy.Matrix:
        A = sympy.zeros(self.n, self.n)
        for i, j in self.edges:
            A[i, j] = 1
            A[j, i] = 1
        return A


def build_graph(topology: str, n: int, *, seed: int | None = None) -> Graph:
    """Construct a graph of the requested topology and size.

    Supported topologies: path, cycle, complete, star, grid2d (n = side
    length, total nodes = n*n), erdos_renyi (seeded, p=0.4).
    """
    edges: list[tuple[int, int]] = []
    if topology == "path":
        nodes = list(range(n))
        edges = [(i, i + 1) for i in range(n - 1)]
    elif topology == "cycle":
        if n < 3:
            raise ValueError("cycle requires n >= 3")
        nodes = list(range(n))
        edges = [(i, (i + 1) % n) for i in range(n)]
    elif topology == "complete":
        nodes = list(range(n))
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    elif topology == "star":
        nodes = list(range(n))
        edges = [(0, i) for i in range(1, n)]
    elif topology == "grid2d":
        side = n
        nodes = list(range(side * side))
        def idx(r, c):
            return r * side + c
        for r in range(side):
            for c in range(side):
                if c + 1 < side:
                    edges.append((idx(r, c), idx(r, c + 1)))
                if r + 1 < side:
                    edges.append((idx(r, c), idx(r + 1, c)))
    elif topology == "erdos_renyi":
        rng = np.random.default_rng(seed if seed is not None else 0)
        nodes = list(range(n))
        p = 0.4
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    edges.append((i, j))
        # guarantee connectivity so kernel(L) is exactly 1-dimensional,
        # which is what the spectral gap / kernel projector test expects
        for i in range(n - 1):
            if (i, i + 1) not in edges and (i + 1, i) not in edges:
                edges.append((i, i + 1))
    else:
        raise ValueError(f"unknown topology '{topology}'")
    return Graph(topology=topology, n=len(nodes), seed=seed, nodes=nodes, edges=edges)


def degree_matrix(A: np.ndarray) -> np.ndarray:
    return np.diag(A.sum(axis=1))


def laplacian(A: np.ndarray) -> np.ndarray:
    """L = D - A (spec section 13)."""
    return degree_matrix(A) - A


def laplacian_exact(A_exact: sympy.Matrix) -> sympy.Matrix:
    n = A_exact.shape[0]
    D = sympy.zeros(n, n)
    for i in range(n):
        D[i, i] = sum(A_exact.row(i))
    return D - A_exact
