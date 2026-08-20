# MASS_SPECTRUM_AUDIT.md

## Dimensional analysis

m_0 must carry the ENTIRE dimensional content [mass] of the formula by itself. The graph/spectral construction supplies only a dimensionless shape (the relative pattern of the sqrt(lambda_n) sequence) -- it cannot, by dimensional analysis alone, supply an absolute mass scale. This is not a flaw specific to this project; it is true of every eigenvalue-ratio mass formula in physics (e.g. Regge trajectories) -- but it means the formula's entire falsifiable content is in the RATIOS m_n/m_1 = sqrt(lambda_n/lambda_1), never in the absolute values, however m_0 is chosen.

## Zero-parameter structural test

zero-parameter structural test: sqrt(lambda_2/lambda_1) vs real tau/mu = 16.8170, across every topology/size the compiler already implements, no fitting

- path_n6: predicted=1.9319, real tau/mu=16.82, residual=14.885
- path_n10: predicted=1.9754, real tau/mu=16.82, residual=14.842
- path_n20: predicted=1.9938, real tau/mu=16.82, residual=14.823
- cycle_n6: predicted=1.0000, real tau/mu=16.82, residual=15.817
- cycle_n10: predicted=1.0000, real tau/mu=16.82, residual=15.817
- cycle_n20: predicted=1.0000, real tau/mu=16.82, residual=15.817
- complete_n6: predicted=1.0000, real tau/mu=16.82, residual=15.817
- complete_n10: predicted=1.0000, real tau/mu=16.82, residual=15.817
- complete_n20: predicted=1.0000, real tau/mu=16.82, residual=15.817
- star_n6: predicted=1.0000, real tau/mu=16.82, residual=15.817
- star_n10: predicted=1.0000, real tau/mu=16.82, residual=15.817
- star_n20: predicted=1.0000, real tau/mu=16.82, residual=15.817
- grid2d_n6: predicted=1.0000, real tau/mu=16.82, residual=15.817
- grid2d_n10: predicted=1.0000, real tau/mu=16.82, residual=15.817
- grid2d_n20: predicted=1.0000, real tau/mu=16.82, residual=15.817

## Erdos-Renyi 50-seed sweep ('go fishing' test)

This ran counter to the expected 'go fishing' outcome and is reported as found, not adjusted after the fact: sweeping 50 random seeds at n=20 did NOT find a materially better match than the fixed path topology (best residual 14.904 vs path_n6's 14.885) -- the sqrt(lambda_2/lambda_1) ratio for random graphs at this size and edge density stays clustered near ~2, essentially the same range as path. This is itself a real, useful negative finding: for adjacent nonzero eigenvalues at modest n, achieving a ratio as large as the real tau/mu=16.8 may not be a matter of hunting through more topologies at fixed size, but could require either much larger n, a qualitatively different eigenvalue-selection rule (not simply 'the 2nd and 3rd nonzero modes'), or a differently normalized Laplacian. This is an open structural question this test surfaces, not one it resolves.

## Degrees-of-freedom verdict

The fixed, parameter-free topologies (path/cycle/complete/star/grid2d) all fail badly at reproducing tau/mu=16.8 from adjacent nonzero eigenvalues (residuals 14.8-15.8 -- cycle/complete/star all have near-degenerate lambda_1~lambda_2, giving a predicted ratio near 1.0, and path gets only to ~2.0). Adding a free random-seed parameter (erdos_renyi, 50 seeds swept) did NOT materially improve this at n=20 -- see erdos_renyi_50_seed_sweep_best_match and its interpretation. So the theoretical 'enough free parameters to fit anything' concern this test was designed to check is NOT what was actually found here: at this graph size, the adjacent-nonzero-eigenvalue ratio appears structurally capped well below the real tau/mu hierarchy regardless of topology or randomization, which is a more specific and more useful negative result than a generic overfitting warning. What remains genuinely unconstrained by the corpus -- and is therefore still an open predictive-content gap, independent of this particular finding -- is any rule for WHICH graph/size represents 'the lepton sector' and WHICH eigenvalues (not necessarily adjacent, not necessarily the 2nd/3rd) map to which generation. Without such a rule, no comparison to real masses is a genuine out-of-sample test.
