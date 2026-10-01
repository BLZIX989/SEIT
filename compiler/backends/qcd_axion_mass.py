"""QCD axion mass relation (flagship-prediction Phase 14 minimal slice).

Implements the standard, established order-of-magnitude QCD axion mass
relation m_a ~ Lambda_QCD^2 / f_a -- not a formula invented by this
repository. This is the exact arithmetic chain independently checked by
hand in reports/master_toe/MASTER_TOE_PREDICTIONS.md ("The one candidate
that passes the format test"), now made executable so it can be run through
compiler/derivation/flagship_theorems.py rather than re-verified by hand.
"""
from __future__ import annotations

from dataclasses import dataclass

LAMBDA_QCD_GEV = 0.200
M_PLANCK_GEV = 1.22e19


@dataclass
class AxionMassResult:
    lambda_qcd_gev: float
    m_planck_gev: float
    n_sub: float
    f_a_gev: float
    m_a_gev: float
    m_a_ev: float


def qcd_axion_mass(
    n_sub: float, *, lambda_qcd_gev: float = LAMBDA_QCD_GEV, m_planck_gev: float = M_PLANCK_GEV,
) -> AxionMassResult:
    """m_a = Lambda_QCD^2 / f_a, with f_a = n_sub * M_Planck (this
    repository's own substitution for the usual Peccei-Quinn scale, per
    SEIT v2.pdf Sec VI)."""
    f_a_gev = n_sub * m_planck_gev
    m_a_gev = lambda_qcd_gev ** 2 / f_a_gev
    return AxionMassResult(
        lambda_qcd_gev=lambda_qcd_gev, m_planck_gev=m_planck_gev, n_sub=n_sub,
        f_a_gev=f_a_gev, m_a_gev=m_a_gev, m_a_ev=m_a_gev * 1e9,
    )
