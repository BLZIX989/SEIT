"""Dimensional/type audit (brief section XII) for the core SEIT chain
equations. Bookkeeping, not computation -- each row states LHS/RHS type
and dimension and whether they typecheck, with an explicit note where a
free scale absorbs all dimensional content (the honest, standard
situation for any dimensionless-graph-derived formula, not a defect)."""
from __future__ import annotations

AUDIT_TABLE = [
    {"equation": "L = D - A", "lhs_type": "matrix (operator on R^n)",
     "dimension": "dimensionless (pure incidence count)", "typechecks": True},
    {"equation": "L phi_n = lambda_n phi_n", "lhs_type": "matrix-vector product = scalar-vector product",
     "dimension": "lambda_n dimensionless (same as L)", "typechecks": True},
    {"equation": "K(t) = exp(-tL)", "lhs_type": "matrix exponential",
     "dimension": "t must be dimensionless too, UNLESS L is reinterpreted as carrying "
                  "[time]^-1 (a physical rate) -- this reinterpretation is asserted, not "
                  "derived, wherever SEIT calls t 'physical time'", "typechecks": "CONDITIONAL"},
    {"equation": "d_t^2(i,j) = sum_k exp(-2 lambda_k t) (phi_k(i)-phi_k(j))^2", "lhs_type": "scalar (squared distance)",
     "dimension": "dimensionless unless g_munu is separately given a [length]^2 scale",
     "typechecks": "CONDITIONAL -- same free-scale issue as m_n=m_0 sqrt(lambda_n)"},
    {"equation": "m_n = m_0 sqrt(lambda_n)", "lhs_type": "scalar [mass]",
     "dimension": "sqrt(lambda_n) dimensionless; m_0 carries the ENTIRE [mass] dimension",
     "typechecks": "TYPECHECKS ONLY IF m_0 supplies the dimension -- see mass_spectrum.py"},
    {"equation": "D_mu = partial_mu + i g A_mu", "lhs_type": "operator [length]^-1",
     "dimension": "[g A_mu] = [length]^-1 forces [g]=[length]^-1/[A_mu] -- standard, "
                  "internally consistent once a convention for [A_mu] is fixed",
     "typechecks": True},
    {"equation": "S = Tr[f(D_Dirac/Lambda)]", "lhs_type": "scalar (action)",
     "dimension": "[S] must be dimensionless (or [energy]x[time] in non-natural units); "
                  "f and Lambda together must be chosen consistently -- no explicit "
                  "convention is fixed anywhere in the corpus for this project's own graphs",
     "typechecks": "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS -- f is left as 'a positive "
                    "even function' with no specific choice tied to this project's own "
                    "D_Dirac construction"},
    {"equation": "G_munu + Lambda g_munu = alpha T_munu", "lhs_type": "rank-2 tensor",
     "dimension": "standard GR dimensional analysis, external established physics, not "
                  "project-specific -- typechecks by the standard convention alpha=8*pi*G/c^4",
     "typechecks": True},
]


def run_audit() -> list[dict]:
    return AUDIT_TABLE
