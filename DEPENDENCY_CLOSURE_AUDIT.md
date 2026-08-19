# Dependency Closure Audit

Determines, for each of the 14 canonical physics branches in scope for the Master Physics
Validation Campaign, whether it is blocked by `CONTINUUM-LIMIT-L-DESI` (the FC-005 Gate 1
node, frozen at `FAIL / RETRIABLE` per `FC005_CHECKPOINT.md`). Raw data:
`DEPENDENCY_CLOSURE_AUDIT.csv`, derived by direct traversal of `object_registry.json` /
`transformation_registry.json`'s `dependency_ids` fields — not asserted.

## Method

A node depends on `CONTINUUM-LIMIT-L-DESI` if that ID appears anywhere in its own
`dependency_ids` or in the `dependency_ids` of any of its ancestors. Direct traversal of the
full registry finds exactly three nodes with `CONTINUUM-LIMIT-L-DESI` (or its own direct
downstream `MATHEMATICAL-CONVERGENCE-DESI`) as an immediate dependency:

```
DESI-SPECTRUM <- CONTINUUM-LIMIT-L-DESI
MATHEMATICAL-CONVERGENCE-DESI <- GRAPH-G-DESI, OPERATOR-L-DESI, CONTINUUM-LIMIT-L-DESI, DESI-SPECTRUM
CURVATURE-CLOSURE-DESI <- MATHEMATICAL-CONVERGENCE-DESI, DESI-HEAT-TRACE, DESI-HEAT-COEFFICIENTS, E-KAPPA-DESI
```

`PHYSICAL-VALIDATION-DESI` depends on `CURVATURE-CLOSURE-DESI`, extending the chain by one
more hop. No other node in the entire registry — across the template chain, Test 1, Test 2,
S^3 control, Fisher-Rao, eigen-uniqueness, or historical T2/NCG bridge — names any FC-005 node
as a dependency.

## Result

**12 of 13 non-DESI branches are NOT blocked by FC-005.** Only branch 12 itself (the DESI
branch) is blocked — trivially, since `CONTINUUM-LIMIT-L-DESI` is its own root failure.

| Branch | Blocked by FC-005? | Why (or why not) |
|---|---|---|
| 1. Variational | No | Blocked instead by `SELECTION-SIGMA` (`OPEN`, unrelated to FC-005) and the fact that no executable backend exists at all |
| 2. Noether/conservation | No | No node registered; not reachable from FC-005 or anything else |
| 3. GR/geometric | No | Same as branch 1 — blocked by the unrelated open `SELECTION-SIGMA` template gate, not FC-005 |
| 4. Matter<->Geometry | No | `SEMICLASSICAL-EINSTEIN-EQUATION` depends on `GEOMETRY-NODE`/`QUANTUM-NODE`, neither of which touches FC-005 |
| 5. Statistical Recovery Core | No | Fisher-Rao branch is fully self-contained, no FC-005 dependency |
| 6. Quantum Recovery Core | No | Eigen-uniqueness counterexample is fully self-contained |
| 7. Thermodynamic Recovery Core | No | Depends on `MATTER-NODE`, unrelated to FC-005 |
| 8. Spectral/heat-kernel math | No | Test 1 and the S^3 control are fully self-contained; confirmed zero dependency edge to any FC-005 node |
| 9. Spectral geometry | No | Test 2 (diffusion-metric pipeline) and the eigenvalue-uniqueness counterexample are self-contained |
| 10. Gauge/representation/matter | No | Blocked by the historical bridge's own explicit "not attempted" status, not FC-005 |
| 11. Cosmological | No | `COSMOLOGY-NODE` is a bare template placeholder unrelated to FC-005; the DESI fiducial-cosmology *parameter file* is consumed by branch 12, not the reverse |
| 12. DESI discrete<->continuum | **Yes (self)** | This is the branch itself |
| 13. Previously falsified | No | Both falsification records are self-contained calculations |

## Conclusion

FC-005 remaining `FAIL / RETRIABLE` **does not block any of the other 12 branches** from being
validated to whatever extent their own executable content supports. The branches that remain
`OPEN`/`PROPOSED`/`NOT REGISTERED` in this campaign's validation matrix
(`MASTER_PHYSICS_VALIDATION_MATRIX.csv`) are blocked by the *absence of an executable backend*
in this compiler build — a separate, independent limitation from FC-005's numerical
non-convergence, and out of scope to fix here (per the campaign's own boundary: no new
backends).
