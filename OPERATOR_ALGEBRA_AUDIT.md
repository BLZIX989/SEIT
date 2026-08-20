# OPERATOR_ALGEBRA_AUDIT.md

## {gamma^mu, gamma^nu} = 2 g^{mu nu} I (Dirac basis, signature (+,-,-,-))

External established mathematics: True
Holds exactly for all 16 (mu,nu) pairs: **True**

## Jacobi identity [T_a,[T_b,T_c]] + [T_b,[T_c,T_a]] + [T_c,[T_a,T_b]] = 0 for T_a = sigma_a/2 (su(2) fundamental representation)

Holds exactly for all 27 (a,b,c) triples: **True**

## Gauge covariant derivative dimensional check

{
  "claim": "D_mu = partial_mu + i g A_mu",
  "[partial_mu]": "[length]^-1",
  "[D_mu]": "[length]^-1 (must match partial_mu for the sum to typecheck)",
  "[g A_mu]": "must equal [length]^-1, so [g] = [length]^-1 / [A_mu]",
  "consequence": [
    "The coupling constant g's dimension is FIXED once a convention for [A_mu] is chosen (e.g. [A_mu]=[length]^-1 in natural units with g dimensionless, the standard QFT convention) -- this is internally consistent standard physics, not a finding specific to this project, included here only because the brief explicitly asked for every major equation's dimensional audit to be performed rather than assumed."
  ]
}
