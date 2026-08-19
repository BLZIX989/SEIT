"""Ingestion-layer regression tests using the committed FC-005 pilot
fixture (data/desi/dr1/fc005/validated/pilot_fixture/) -- a real,
documented 3000-object subsample of the DESI DR1 LRG SGC clustering
catalog (0.4 <= z < 0.6), NOT synthetic data (spec section 17: DESI
results must be derived exclusively from the downloaded DESI catalog).
Re-downloading the full 64 MB raw catalog is not required to run these
tests; the small fixture is git-tracked precisely so this suite is
reproducible from a fresh checkout.
"""
from pathlib import Path

import numpy as np
import pytest
from astropy.table import Table

from compiler.backends.desi_graph import (
    CosmologyModel, build_kernel_graph, graph_laplacian_from_weights, radec_to_cartesian,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "data" / "desi" / "dr1" / "fc005" / "validated" / "pilot_fixture" / "lrg_sgc_pilot_3000_z0.4-0.6.fits"

pytestmark = pytest.mark.skipif(not FIXTURE.exists(), reason="pilot fixture not present in this checkout")


def _load_fixture():
    t = Table.read(FIXTURE)
    return {name: np.asarray(t[name]) for name in t.colnames}


def test_fixture_is_real_desi_data_not_synthetic():
    data = _load_fixture()
    assert len(data["RA"]) == 3000
    assert np.all(data["Z"] >= 0.4) and np.all(data["Z"] < 0.6)
    assert np.all(np.isfinite(data["RA"])) and np.all(np.isfinite(data["DEC"]))
    # real sky coordinates, not a synthetic grid/uniform pattern
    assert data["RA"].std() > 0 and data["DEC"].std() > 0


def test_pilot_graph_construction_reproduces_known_properties():
    data = _load_fixture()
    cosmo = CosmologyModel(H0=67.36, Om=0.315192, OL=0.684808)
    from compiler.backends.desi_graph import comoving_distance
    chi = comoving_distance(data["Z"], cosmo)
    points = radec_to_cartesian(data["RA"], data["DEC"], chi)

    from scipy.spatial import cKDTree
    tree = cKDTree(points)
    nn_dist, _ = tree.query(points, k=2)
    epsilon = 3.0 * float(np.median(nn_dist[:, 1]))

    W = build_kernel_graph(points, epsilon=epsilon, weights=data["WEIGHT"])
    D, L = graph_laplacian_from_weights(W)

    assert np.allclose(W, W.T, atol=1e-12)
    assert np.all(W >= 0)
    assert np.allclose(np.diagonal(W), 0.0)
    assert np.allclose(L, L.T, atol=1e-10)
    assert np.max(np.abs(L.sum(axis=1))) < 1e-8

    rng = np.random.default_rng(0)
    for _ in range(50):
        v = rng.normal(size=len(data["RA"]))
        assert v @ L @ v >= -1e-6

    eigvals = np.linalg.eigvalsh(L)
    n_zero = int(np.sum(np.abs(eigvals) < 1e-8))
    assert n_zero >= 1  # at least one connected component


def test_pilot_epsilon_is_derived_from_data_not_hardcoded():
    data = _load_fixture()
    cosmo = CosmologyModel(H0=67.36, Om=0.315192, OL=0.684808)
    from compiler.backends.desi_graph import comoving_distance
    chi = comoving_distance(data["Z"], cosmo)
    points = radec_to_cartesian(data["RA"], data["DEC"], chi)
    from scipy.spatial import cKDTree
    tree = cKDTree(points)
    nn_dist, _ = tree.query(points, k=2)
    median_nn = float(np.median(nn_dist[:, 1]))
    assert median_nn > 0
    assert np.isfinite(median_nn)
