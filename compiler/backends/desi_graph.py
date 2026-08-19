"""Discrete-observation -> continuum operator bridge, spec sections
9-12 of the FC-005 build command: G_DESI -> L_DESI -> L_tilde_(N,eps).

This module implements the pipeline as reusable functions operating on
any (ra, dec, z[, weights]) catalogue. It is exercised in this build's
test suite ONLY on synthetic point clouds, explicitly to verify the code
is correct (graph symmetry, PSD-ness, row-sum-zero, normalization
bookkeeping) -- never as a stand-in for an actual DESI result. No DESI
catalogue (positions/redshifts/weights) was found anywhere in the
repository or the supplied workbooks during this build's audit; the
'FC-005 Full Execution Index' sheet of the primary source workbook
records this itself ("No catalog file present in uploaded workbook").
G_DESI is therefore registered OPEN / PENDING DATA in the IR -- this
module's functions are the not-yet-invoked machinery for when a real
catalogue becomes available, not a substitute result.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad


@dataclass
class CosmologyModel:
    H0: float  # km/s/Mpc
    Om: float
    OL: float
    Ok: float = 0.0
    c_km_s: float = 299792.458

    def E(self, z: float) -> float:
        return np.sqrt(self.Om * (1 + z) ** 3 + self.Ok * (1 + z) ** 2 + self.OL)

    @classmethod
    def from_yaml(cls, path) -> "CosmologyModel":
        """Loads the recorded, provenance-tracked cosmology (spec section
        12: never silently use arbitrary cosmological parameters). See
        FC005_cosmology.yaml for the source citation."""
        import yaml
        with open(path) as f:
            config = yaml.safe_load(f)
        p = config["parameters"]
        return cls(H0=p["H0_km_s_Mpc"], Om=p["Omega_m"], OL=p["Omega_Lambda"], Ok=p["Omega_k"])


def comoving_distance(z: np.ndarray, cosmology: CosmologyModel) -> np.ndarray:
    """chi(z) = c * integral_0^z dz' / H(z'), H(z') = H0 * E(z')."""
    z = np.atleast_1d(np.asarray(z, dtype=float))
    out = np.empty_like(z)
    for i, zi in enumerate(z):
        val, _ = quad(lambda zp: 1.0 / cosmology.E(zp), 0.0, zi)
        out[i] = cosmology.c_km_s / cosmology.H0 * val
    return out


def radec_to_cartesian(ra_deg: np.ndarray, dec_deg: np.ndarray, chi: np.ndarray) -> np.ndarray:
    ra = np.radians(np.asarray(ra_deg, dtype=float))
    dec = np.radians(np.asarray(dec_deg, dtype=float))
    x = chi * np.cos(dec) * np.cos(ra)
    y = chi * np.cos(dec) * np.sin(ra)
    z_sp = chi * np.sin(dec)
    return np.stack([x, y, z_sp], axis=-1)


def catalogue_to_points(
    ra_deg: np.ndarray, dec_deg: np.ndarray, z: np.ndarray, cosmology: CosmologyModel,
) -> np.ndarray:
    chi = comoving_distance(z, cosmology)
    return radec_to_cartesian(ra_deg, dec_deg, chi)


def gaussian_kernel_C_K(d: int) -> float:
    """C_K for the isotropic Gaussian kernel K(u) = exp(-||u||^2/2), u in
    R^d: C_K = integral K(||u||^2) u_1^2 du = (2*pi)^(d/2), by separability
    (each of the d independent 1D Gaussian integrals contributes
    sqrt(2*pi), and one of them carries the extra u_1^2 moment, which for
    a standard normal is also sqrt(2*pi) since Var=1). Verified
    numerically in compiler/tests/test_fc005_desi_graph.py.
    """
    return (2 * np.pi) ** (d / 2)


def build_kernel_graph(points: np.ndarray, epsilon: float, weights: np.ndarray | None = None) -> np.ndarray:
    """W_ij = K(d_ij^2 / eps^2) with the Gaussian kernel K(u)=exp(-u/2);
    optional per-point observational weights (w_FKP, w_sys, ...) enter
    multiplicatively, W_ij *= w_i * w_j, as is standard for weighted
    pair-counting kernels; W_ii is set to 0 (no self-loops)."""
    diff = points[:, None, :] - points[None, :, :]
    d2 = np.sum(diff ** 2, axis=-1)
    W = np.exp(-d2 / (2 * epsilon ** 2))
    np.fill_diagonal(W, 0.0)
    if weights is not None:
        w = np.asarray(weights, dtype=float)
        W = W * w[:, None] * w[None, :]
    return W


def graph_laplacian_from_weights(W: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    D = np.diag(W.sum(axis=1))
    L = D - W
    return D, L


def normalize_continuum_limit(L_N: np.ndarray, N: int, epsilon: float, *, d: int = 3, C_K: float | None = None) -> np.ndarray:
    """L_tilde_(N,eps) = -L_N / (C_K * N * eps^(d/2 + 1)); d=3 gives the
    eps^(5/2) normalization the workbook records explicitly (EQ-014)."""
    if C_K is None:
        C_K = gaussian_kernel_C_K(d)
    return -L_N / (C_K * N * epsilon ** (d / 2 + 1))
