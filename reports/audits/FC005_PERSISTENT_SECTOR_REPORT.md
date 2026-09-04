# FC005_PERSISTENT_SECTOR_REPORT.md

Test graph: erdos_renyi(n=60, seed=0)

| lambda_c (frac of max) | n modes | P idempotent | P self-adjoint | L_Pi = P.L.P verified | K_Pi monotone decreasing |
|---|---|---|---|---|---|
| lambda_c_frac_0.1 | 1 | True | True | True | True |
| lambda_c_frac_0.25 | 1 | True | True | True | True |
| lambda_c_frac_0.5 | 8 | True | True | True | True |

## Persistent distance beta-limit behavior

beta->0 matches unweighted persistent distance: **True**
Monotone nonincreasing in beta: **True**

beta cannot be taken to infinity for a nontrivial geometry -- confirmed here: d(20.0) = 0.237636, approaching but not exactly reaching 0 for finite beta, consistent with beta acting as a finite coarse-graining scale rather than a limit to be maximized.
