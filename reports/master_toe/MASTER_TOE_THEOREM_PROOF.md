# Master TOE Theorem — Proof / Derivation Detail

Companion to `MASTER_TOE_THEOREM.md`. Full derivation chain for both surviving results, with
exact provenance.

## Theorem 1: the graph-Laplacian spectral cascade

This proof is not new to this campaign — it is reproduced here for completeness, exactly as
already established in this project's canonical code and reports.

1. **L = D − W is symmetric PSD.** For weights W_ij ≥ 0 symmetric, and D = diag(row sums of W):
   for any real vector v, v^T L v = ½ Σ_ij W_ij (v_i − v_j)² ≥ 0, and L = L^T by construction of
   D and W. Verified directly on real data: `L_symmetric=True`, `vTLv_min_over_200=4753.9` (200
   random test vectors, DESI N=2500 sample) — `compiler/backends/desi_diagnostics.py::audit_graph`.
2. **Eigendecomposition exists and is real.** Symmetric real matrices are orthogonally
   diagonalizable (spectral theorem, standard linear algebra) — `Lψ_n = λ_nψ_n`,
   `compiler/backends/spectral.py`.
3. **Heat-flow / heat-trace.** `R(t) = exp(−tL)`, `K(t) = Σ_n exp(−tλ_n)` — well-defined since all
   `λ_n ≥ 0` (step 1) — `compiler/backends/heat_flow.py`.
4. **S³ analytic limit.** Comparison against the known closed-form S³ heat-kernel coefficients
   (a₀, a₁, a₂), fit at degrees 2, 4, 5 across 4 fit windows: residual |E_κ| shrinks from ~10⁻³ at
   degree 2 to ~10⁻⁸–10⁻⁹ at degree 4–5, confirming numerical convergence to the analytic result
   — `compiler/backends/heat_kernel_sphere.py`, `CALC-FC005-S3-CONTROL` (VERIFIED).

Every step re-executed twice this campaign (via `python3 -m pytest compiler/tests -q`, 95 passed)
and confirmed bit-for-bit reproducible against the pre-campaign state.

## Theorem 2: Noether's theorem as the conservative special case of a (D,T,C) category

Full derivation as given in `DTC_Formal_Structure.docx` §3.1, independently checked this
campaign:

1. **Setup.** Let 𝒟 be the category whose objects are physical states of a system and whose
   morphisms are the time-evolutions the system's dynamics admit.
2. **Continuous symmetry, categorically.** A continuous symmetry is a one-parameter group of
   automorphisms of 𝒟 that commutes with time-evolution — equivalently, a subgroup of
   structure-preserving self-maps leaving the realized subcategory 𝒞 ⊆ 𝒟 invariant.
3. **Noether's theorem, standard form.** For a Lagrangian system, the Euler-Lagrange equations
   and the calculus of variations applied to a one-parameter group action prove: such a symmetry
   forces the existence of a function on phase space constant along every trajectory in 𝒞.
4. **Identification with categorical "retention."** A quantity constant along every morphism in
   𝒞 with a given domain is exactly the categorical definition of a *retained* object (§2.3 of
   the same document: an object A is retained under 𝒞 when every morphism in 𝒞 with domain A has
   codomain isomorphic to A). Step 3's conserved quantity is precisely such an invariant.
5. **Conclusion.** The mapping is exact — no new machinery is introduced; Noether's own proof
   (already rigorously established for Lie group actions on symplectic manifolds, independent of
   this project) is simply re-expressed in category-theoretic vocabulary, with the categorical
   "retention" concept shown to coincide with the physical "conserved quantity" concept in this
   one regime.

**Why this does not generalize** (the reason Theorem 2 is exactly Noether's theorem and nothing
more): step 3 requires a continuous (Lie) symmetry group with an infinitesimal generator, and a
variational (Lagrangian) structure on 𝒞. A subcategory 𝒞 built from discrete admissible morphisms
only, with no continuous structure, has no infinitesimal generator — the calculus-of-variations
machinery that produces the conserved current has nothing to act on. `DTC_Formal_Structure.docx`
states this precisely (§3.2) and this campaign found no alternative, non-variational argument
anywhere in the corpus that supplies a substitute mechanism.

## Both proofs are external mathematics/physics, not new SEIT-original physical content

Per the campaign's own status-semantics discipline: Theorem 1 was already `VERIFIED` (canonical,
independently executed) prior to this campaign. Theorem 2 is a correct re-derivation of an
already-135-year-old (1918) established physics theorem in different notation — recorded here as
`RECOVERED` (external result, exactly and correctly reproduced), never as `DERIVED` in the sense
of new physical content, per this campaign's status semantics (Part 39 of the campaign
specification: "Do not collapse these statuses").
