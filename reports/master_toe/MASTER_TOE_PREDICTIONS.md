# Master TOE Predictions

Per campaign section 41: a genuine TOE must eventually produce outputs not used as inputs. This
report searches the corpus and this campaign's own results for anything meeting that bar, and is
explicit about the one rule that disqualifies most of what was found: **never use an observed
quantity as both input and prediction.**

## Disqualified: the fine-structure constant and electron mass (`DTC COMPILER.docx`)

Both fail the input/prediction separation rule outright — see `MASTER_TOE_FALSIFICATION_REPORT.md`
§1–2. The "predicted" values are the already-measured CODATA values; the claimed derivations do
not independently arrive at them. These are not predictions. They are restated inputs.

## The one candidate that passes the format test: SEIT v2's three-prediction set

`SEIT v2.pdf` §VI registers three specific, numerical, **not-yet-independently-observed** claims:

| Prediction | Value | Test |
|---|---|---|
| Persistence Axion mass | m_aP ≈ 6.885×10⁻¹³ eV | direct axion search / astrophysical bounds on ultralight axion dark matter |
| Monochromatic gravitational-wave background | 166.48 Hz | LIGO/Virgo stochastic background search (audio band) |
| Dwarf-spheroidal soliton core radius | 120–150 parsecs (Fornax, Sculptor, et al.) | dwarf-spheroidal galaxy kinematic surveys |

**Why this is structurally different from the α/m_e claims**: none of these three target
quantities is an already-measured constant being restated. The axion mass uses the real, standard
QCD-axion mass relation m_a ~ Λ²_QCD/f_a (a genuine established physics formula, not invented
here), substituting the document's own quantity N_sub·M_Planck for the usual Peccei-Quinn scale
f_a. This campaign independently recomputed the full arithmetic chain:

```
N_sub = 4.7619
m_aP = (0.200 GeV)² / (4.7619 × 1.22×10¹⁹ GeV) = 6.885×10⁻²² GeV = 6.885×10⁻¹³ eV
```

This checks out exactly against the stated inputs (Λ_QCD ≈ 0.2 GeV and M_Planck ≈ 1.22×10¹⁹ GeV
are both correct, standard values). The document states "this is not a fitted parameter. It is
derived from two measured quantities (Λ_QCD and M_Pl) and one geometrically fixed quantity
(N_sub)."

## What was NOT verified this campaign (the honest gap)

1. **The N_sub ← n_s (CMB spectral index) connecting formula.** The document states N_sub =
   4.7619 is fixed "from CMB spectral index constraint" (using the real, measured Planck value
   n_s = 0.965), but the specific formula mapping n_s to N_sub was not located in the text this
   campaign read. Until that formula is located and checked, it cannot be confirmed whether N_sub
   is genuinely, independently derived from n_s (making the axion-mass prediction genuine) or
   itself reverse-fit to produce a "nice" downstream number (making it another instance of the
   §1–2 pattern). **This is the single highest-priority follow-up identified by this campaign.**
2. **Comparison against current observational constraints.** This campaign did not check the
   three predicted values against:
   - current axion/ultralight-dark-matter search exclusion limits (a mass of ~7×10⁻¹³ eV sits in
     the "fuzzy dark matter" mass window explored by some current experiments and cosmological
     structure-formation bounds, but whether this specific value is already excluded was not
     checked);
   - current LIGO/Virgo stochastic gravitational-wave background upper limits at 166.48 Hz;
   - published dwarf-spheroidal (Fornax, Sculptor, etc.) dark-matter core-radius measurements.

   None of these checks require inventing new physics — they require looking up already-published
   observational results, which this campaign did not perform within its scope.

## Disposition

**Not promoted, not dismissed.** This is recorded as an open, structurally legitimate, partially-
verified prediction set — the strongest candidate for a genuine "output not used as input" found
anywhere in this corpus — pending the two follow-up checks above. No canonical registry entry has
been created for it.

## Everything else

No other document read this campaign, and no grep sweep of the ~20 documents not read in depth,
surfaced any other candidate numerical prediction with a comparably legitimate structure. Most
corpus documents that discuss "predictions" or "falsification criteria" (e.g., Functorial Gauge
Unification's "Rigid Falsification Protocols") do not name an operationally measurable quantity —
see `MASTER_TOE_FALSIFICATION_REPORT.md` §5.
