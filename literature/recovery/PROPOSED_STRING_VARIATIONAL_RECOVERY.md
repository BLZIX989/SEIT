# Proposed String Variational Recovery

Part VIII of the L0-ST specification. Every structure below carries
`STATUS = PROPOSED_EXTERNAL_RECOVERY`. **None of this is promoted into the canonical
`VARIATIONAL-NODE`.** It is an external, source-backed implementation template only.

## The requested action, confirmed present

The specification asked whether the supplied corpus contains

```
S[X] = -1/(2π α') ∫ d²σ √(-h) h^{ab} ∂_a X^μ ∂_b X_μ
```

and/or the Nambu-Goto equivalent. **Confirmed present in both sources**, independently:

- Tong, *String Theory*, eq. (1.22): `S = -1/(4πα') ∫ d²σ √(-g) g^{αβ} ∂_α X^μ ∂_β X^ν η_μν`
- Kiritsis, *Introduction to Superstring Theory*, eq. (3.2.12): `S_P = -(T/2) ∫ d²ξ √(-det g) g^{αβ} ∂_α X^μ ∂_β X^ν η_μν`

These are the same action up to normalization convention (`T = 1/(2πα')`, Tong eq. 1.17) and
worldsheet-metric variable naming (`g` vs. `h`). The requested equation is **not** a paraphrase or
approximation — it is the literal Polyakov action, confirmed twice, independently.

The Nambu-Goto equivalent is also present in both: Tong eq. (1.13)/(1.14), Kiritsis eq.
(3.2.1)/(3.2.4).

## 1. Action

`S_P = -1/(4πα') ∫ d²σ √(-g) g^{αβ} ∂_α X^μ ∂_β X^ν η_μν` (Tong 1.22). STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 2. Fields

`X^μ(σ,τ)`, `μ = 0,...,D-1` (embedding coordinates, spacetime scalars from the worldsheet
viewpoint) and `g_αβ(σ,τ)` (independent dynamical worldsheet metric). STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 3. Independent variables

Worldsheet coordinates `σ^α = (τ,σ)`, `α=0,1`. STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 4. Variation

`δS/δg^{αβ} = 0` yields the worldsheet metric's own equation of motion, `g_αβ = 2f(σ) ∂_αX·∂_βX`
(Tong 1.24-1.25), showing `g_αβ` is proportional to the induced metric `γ_αβ` up to the conformal
factor `f`, which drops out of the `X`-equation of motion. STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 5. Euler-Lagrange equations

`∂_α(√(-g) g^{αβ} ∂_β X^μ) = 0` (Tong 1.23; Kiritsis 3.2.15, in the general-target-metric form).
In conformal gauge this reduces to the free 2D wave equation `∂_+∂_- X^μ = 0` (Tong, unnumbered
after 1.4; Kiritsis 3.2.34). STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 6. Constraints

`T_αβ = 0` (the Virasoro constraints), equivalently `(Ẋ ± X')² = 0` (Tong 1.4.1; Kiritsis
3.2.35-3.2.37) — the residual equations of motion for `g_αβ` after gauge-fixing, "the analog of
the Gauss law in the string case" (Tong, verbatim). STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 7. Symmetries

Three, of different character (Tong 1.3.1; Kiritsis 3.2.18-3.2.24), independently confirmed in
both sources:
- **Poincaré invariance** — global spacetime symmetry, `X^μ → Λ^μ_ν X^ν + c^μ`.
- **Reparametrization invariance** (diffeomorphisms) — gauge symmetry on the worldsheet.
- **Weyl invariance** — gauge symmetry special to exactly 2 worldsheet dimensions, `g_αβ →
  Ω²(σ) g_αβ`.

STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 8. Conserved quantities

Momentum `P_μ^α = -T√(det g) g^{αβ} ∂_β X_μ` and angular momentum `J_μν^α` (Kiritsis 3.2.43-3.2.44),
constructed explicitly via the Noether procedure from the symmetries in item 7, with an explicit
proof of `∂_α P_μ^α = 0` using the equations of motion (Kiritsis 3.2.45-3.2.46; Tong's parallel
construction, unnumbered, p.18). STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 9. Gauge redundancies

Reparametrization (2 functions worth) + Weyl (1 function worth) together let the
`d(d+1)/2 = 3`-component 2D worldsheet metric be fixed entirely to `η_αβ` (conformal gauge, Tong
1.27-1.28; Kiritsis 3.2.24) — the counting `d(d+1)/2 - d - 1 = 0` for `d=2` is shown explicitly to
be special to two dimensions (Tong 3.2.31). STATUS = PROPOSED_EXTERNAL_RECOVERY.

## 10. Quantization procedure

**Not extracted this phase.** Canonical quantization of the string (Tong Ch.2, Kiritsis Ch.4) was
not read. Only the classical, pre-quantization Poisson-bracket algebra of the oscillator modes
(Kiritsis 3.3.16-3.3.17, 3.3.27 — the classical Virasoro algebra) was read, which is the direct
precursor to (but not itself) quantization. STATUS = NOT EXTRACTED (honestly reported gap, not a
fabricated placeholder).

## What this recovery is and is not

This is a **complete, source-backed, twice-cross-confirmed implementation template** for "how to
build an action, vary it, derive equations of motion, identify symmetries, and construct
conserved currents" — exactly the missing piece the canonical `VARIATIONAL-NODE` lacks. It is
**not** a derivation of any UOC-specific result: the fields (`X^μ`, `g_αβ`), the physical content
(a relativistic string, not a UOC field), and the symmetry group (Poincaré, assumed rather than
derived from any UOC first principle) are all external to this project. Per Part XVII of the
L0-ST specification, **this document does not modify `VARIATIONAL-NODE`, does not rewrite the
MDCL, and does not promote anything into canonical state.** See
`literature/recovery/STRING_THEORY_PROPOSED_RECOVERIES/RECOVERY-STR-001.json` for the formal
recovery-specification record derived from this template.
