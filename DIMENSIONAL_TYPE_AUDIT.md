# DIMENSIONAL_TYPE_AUDIT.md

| Equation | Dimension/type note | Typechecks |
|---|---|---|
| `L = D - A` | dimensionless (pure incidence count) | True |
| `L phi_n = lambda_n phi_n` | lambda_n dimensionless (same as L) | True |
| `K(t) = exp(-tL)` | t must be dimensionless too, UNLESS L is reinterpreted as carrying [time]^-1 (a physical rate) -- this reinterpretation is asserted, not derived, wherever SEIT calls t 'physical time' | CONDITIONAL |
| `d_t^2(i,j) = sum_k exp(-2 lambda_k t) (phi_k(i)-phi_k(j))^2` | dimensionless unless g_munu is separately given a [length]^2 scale | CONDITIONAL -- same free-scale issue as m_n=m_0 sqrt(lambda_n) |
| `m_n = m_0 sqrt(lambda_n)` | sqrt(lambda_n) dimensionless; m_0 carries the ENTIRE [mass] dimension | TYPECHECKS ONLY IF m_0 supplies the dimension -- see mass_spectrum.py |
| `D_mu = partial_mu + i g A_mu` | [g A_mu] = [length]^-1 forces [g]=[length]^-1/[A_mu] -- standard, internally consistent once a convention for [A_mu] is fixed | True |
| `S = Tr[f(D_Dirac/Lambda)]` | [S] must be dimensionless (or [energy]x[time] in non-natural units); f and Lambda together must be chosen consistently -- no explicit convention is fixed anywhere in the corpus for this project's own graphs | NOT COMPUTABLE FROM AVAILABLE DEFINITIONS -- f is left as 'a positive even function' with no specific choice tied to this project's own D_Dirac construction |
| `G_munu + Lambda g_munu = alpha T_munu` | standard GR dimensional analysis, external established physics, not project-specific -- typechecks by the standard convention alpha=8*pi*G/c^4 | True |
