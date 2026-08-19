# Master TOE Falsification Report

Per campaign section 35: every candidate structure found in the historical corpus was attacked,
not merely summarized. This report documents each falsification attempt and its result, plus the
already-standing falsifications this campaign confirms are still in force.

## 1. FALSIFIED: the fine-structure-constant "derivation" (`DTC COMPILER.docx` §5.1)

**Claim**: α = Vol(S¹)/Vol(CP²) = 2π/(π²/2) = 4/π, which the document then states "maps to the
exact measured inverse value α⁻¹ ≈ 137.035999."

**Test applied**: direct arithmetic recomputation.

**Result**: 2π/(π²/2) = 4/π ≈ 1.2732. This is neither 137.035999 nor its reciprocal (π/4 ≈
0.7854). No algebraic step, normalization formula, or intermediate calculation is shown anywhere
in the source text connecting the computed geometric ratio to the asserted measured value — the
two numbers are stated adjacent to each other with a vague, unquantified appeal to "the localized
normalization scale of the running coupling constant at low energy bounds." **FALSIFIED as a
derivation.** The individual geometric facts used (Vol(S¹)=2π, Vol(CP²)=π²/2) are correct; the
claimed connection to the physical constant is not.

**Corroborating evidence**: `DTC_Rosetta_Stone_TOE_v2.docx` §10 (a separate document, same
research program, presumably earlier) explicitly states: "It does not derive the fine-structure
constant... Whether these are further necessity-forced quantities or genuinely free parameters...
is unresolved." This directly contradicts `DTC COMPILER.docx`'s later claim of an "exact
analytical derivation" — an internal corpus inconsistency this campaign notes as corroboration,
not as the primary evidence (the arithmetic check stands on its own).

## 2. FALSIFIED (as an independent derivation): the electron-mass eigenvalue (`DTC COMPILER.docx` §5.2)

**Claim**: λ₁ = m_e/M_Planck = 4.18575×10⁻²³, obtained by "evaluating the constrained boundary
condition of the hypergraph's stable topological twists."

**Test applied**: direct arithmetic recomputation of λ₁ × M_Planck.

**Result**: 4.18575×10⁻²³ × 2.17643×10⁻⁸ kg = 9.110×10⁻³¹ kg, matching the document's own quoted
electron mass (9.10938×10⁻³¹ kg) to 4 significant figures. This is exactly what would result from
computing λ₁ directly as m_e/M_Planck using the two already-known, already-measured constants. No
operator, boundary condition, or eigenvalue computation of any kind is shown anywhere in the
source text that would justify the stated number by any route other than this direct division.
**Treated as FALSIFIED as a claimed independent, first-principles derivation** — the number is
numerically indistinguishable from a reverse-computation, and no evidence in the text rules that
out.

**Pattern match**: this is the identical practice already identified and rejected in the
unrelated Hashimoto "Theory of Everything" PDF during this project's prior L0 literature-ingestion
phase — choose or compute a free parameter specifically so that a downstream quantity matches an
already-known measured value, then present the match as proof of a first-principles derivation.
This project's own Master Physics Validation Campaign already prohibits exactly this practice
(Part I.3: "fit the desired physical result and then declare it recovered; promote a numerical
coincidence to a derivation").

## 3. REJECTED (mathematically ill-posed): the emergent-metric construction (Master Equation Codex §3.2)

**Claim**: g_ij = lim_{x'→x} ∂²d/∂x^i∂x'^j, where d(i,j) is the graph diffusion distance between
discrete nodes i, j.

**Test applied**: dimensional/well-formedness check.

**Result**: differentiating d(i,j) with respect to continuous coordinates x^i presupposes a
smooth embedding of the discrete graph nodes into a continuous coordinate space — an embedding
that is never constructed anywhere in the shown text. This is exactly the non-uniqueness problem
this project's own Test 2 pipeline independently found and correctly marked `METRIC-CANDIDATE =
CONDITIONAL` (not derived). The document presents this step as already completed; it is not.
**Not promotable as written.**

## 4. CONTRADICTED by this project's own execution: "quantum mechanics is the continuum limit of the spectral graph" (Master Equation Codex §6)

**Claim**: "Equation 6.2 is the continuum limit of Eq. 1.2 (Lψ_n=λ_nψ_n). The Hamiltonian Ĥ is
the continuum image of the graph Laplacian L," stated as a general, unconditional fact.

**Test applied**: comparison against this project's own FC-005 sparse N-scaling investigation
(real DESI DR1 data, N up to 64,000).

**Result**: this project's own rigorously executed FC-005 campaign found genuine joint
eigenvalue+eigenvector convergence for only the lowest ~4 of 15 tested spectral modes, even in the
best-behaved synthetic control (uniform IID sampling), and explicit non-convergence for the
remainder. A general, unconditional continuum-limit claim of the kind stated here is inconsistent
with this project's own hard-won empirical finding. **Not accepted as a general claim.**

## 5. NOT SUBSTANTIATED (no isomorphism constructed): Functorial Gauge Unification's TOE-completion claim

**Claim**: "The search for a Theory of Everything is complete" — string theory, Loop Quantum
Gravity, and AdS/CFT are asserted to be "different coordinate dialects of the same underlying
algebraic Topos," proved via a claimed functorial isomorphism T.

**Test applied**: full-document read (93 lines) searching for any constructed map, proof, or
intermediate calculation connecting the four frameworks' quoted (individually correct) formulas.

**Result**: none found. Each "unification" consists of stating a real, correctly-quoted formula
from one established framework next to a real, correctly-quoted formula from another, and
asserting equivalence. The document's own "Rigid Falsification Protocols" (e.g., "the calculated
adaptive multiplicity vector is zero and the system survives") do not name a measurable quantity
or describe an actual experiment, so the document's own claim to be falsifiable does not hold up
on inspection either. **Rejected**, and additionally inconsistent with the well-documented,
genuinely open status of quantum-gravity unification in mainstream physics.

## 6. Already-standing falsifications this campaign confirms remain in force

- **`FALS-FC005-FISHER-LORENTZIAN`** — the Fisher-Rao metric cannot carry a Lorentzian signature
  under any basis change (PSD matrix, permanent obstruction). Unaffected by this campaign.
- **`FALS-FC005-EIGENVALUE-UNIQUENESS`** — spectrum alone does not uniquely determine an operator
  (explicit 2×2 counterexample, matching spectra, distinct matrices). Unaffected by this campaign;
  directly relevant context for evaluating any corpus claim that treats `Spec(L)` as if it
  uniquely determined downstream physical structure (several do, uncritically).

## 7. Confirmed absent (not newly falsified, but independently reconfirmed): the named obstruction artifacts

`compiler/historical/register.py` already registered, in a prior phase of this project, that no
file in the repository contains the "abelian bridge obstruction," "asymmetric-abelian
obstruction," or "non-Abelian commutant obstruction" proof artifacts that other project
instructions have referenced by name. This campaign re-ran that search via `grep` across the
freshly full-text-extracted content of all ~30 corpus documents (not merely the DOCX-to-text
conversion available at the time of the original audit) and confirms: still absent, everywhere.

## 8. One test that did NOT produce a falsification: DTC-RP-004's own self-test

`DTC-RP-004_Forced_vs_Free.docx` ran its own honest negative test (its proposed NCG-spectral-
action correspondence coefficient γ is not "forced" by the underlying spectral data) using the
real, correctly-stated 2007/2012 Chamseddine-Connes-Marcolli Higgs-mass historical episode as its
calibration standard. This campaign independently confirmed the historical facts cited are
accurate and the logical structure of the test is sound. **This is not a falsification of
anything** — it is the corpus's own author correctly falsifying their own weaker claim, and
reporting it honestly. It is recorded here as the methodological standard the rest of the corpus
should be, and mostly is not, held to.
