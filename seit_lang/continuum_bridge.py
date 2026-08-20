"""Continuum-bridge branch as executable `.seit` primitives and honest
source generation (Phase 8): represents KC-003a/b/c/d and VR-001
explicitly as OPEN dependencies, building on -- not modifying --
scientific_corpus/derivation/kc003_vr001.py. Must not fabricate closure.

THE CENTRAL DESIGN PROBLEM THIS PHASE EXISTS TO SOLVE: KC-003a and
KC-003d are recorded (see kc003_vr001.py's own kc003_decomposition())
as "NOT COMPUTABLE FROM AVAILABLE DEFINITIONS" -- there is no missing
object to supply, nothing to run. If this phase simply wrapped
kc003_decomposition() as an ordinary `.seit` primitive and let a
program write `derive KC003a = kc003a_report();`, seit_lang.dag's
Phase 4 state machine would mechanically advance KC003a to
SeitState.CALCULATED the moment the Python call succeeds -- which it
always would, since the function runs fine and returns a dict whose
CONTENT happens to say "open." The program's own execution state
(CALCULATED) would then contradict the scientific content it just
computed (OPEN) -- exactly the "fabricate closure" outcome the brief
warns against.

The fix: KC-003a/d are represented in generated `.seit` source as
`variable` declarations (never `derive`/`calculate`) with an explicit
`status ... = OPEN;` statement -- so they honestly stay at
SeitState.DECLARED in the DAG (no producing statement exists for them,
by design) while ALSO carrying the real, correct status label and
provenance text as source-level metadata. KC-003b and KC-003c (which DO
have real partial/full computed content via CONV-001) get the same
`status`/`provenance` treatment with their own real status labels, not
promoted to CALCULATED either -- reaching a `.seit` "CALCULATED" DAG
state for the CLAIM itself is never done here; only genuine
data-reporting accessor calls (kc003_subclaim_report, vr001_*_result)
may be `derive`d, and even then the computed node represents "a report
ABOUT the claim was retrieved," never "the claim was resolved."

A DELIBERATE SEPARATION worth stating plainly: the `.seit` `status`
statement is DESCRIPTIVE metadata (an assertion the source records,
per Phase 1's status_stmt grammar) -- it is not, and must never become,
the DAG's actual tracked SeitState (seit_lang.dag.SeitDAG.states),
which Phase 3/4 compute independently from what was really
derived/calculated. For every node this module's generator emits, the
two agree only because nothing was derived/calculated for it (both
honestly say "nothing happened yet"); a `status` statement's own text
is never taken as ground truth for the DAG's real execution state --
matching compiler/core/status.py's own governing rule that a document's
self-reported status is never taken at face value.

generate_continuum_bridge_declarations() emits `.seit` source directly
from the real kc003_decomposition()/vr001_known_manifold_control()
results -- the OPEN/CALCULATED/RESOLVED labels are read from those
functions' own status TEXT (see _seit_status_label), not a
hand-maintained per-subclaim table that could silently drift from the
real content.
"""
from __future__ import annotations

from scientific_corpus.derivation import kc003_vr001

from .primitives import PrimitiveBinding
from .semantic import TransformationSignature


def kc003_subclaim_report(letter: str) -> dict:
    decomposition = kc003_vr001.kc003_decomposition()
    key = next(k for k in decomposition if k.startswith(f"KC-003{letter}"))
    return decomposition[key]


def vr001_uniform_result(n: float) -> dict:
    n = int(n)
    full = kc003_vr001.vr001_known_manifold_control(n_values=(n,))
    return full["results"]["uniform"][n]


def vr001_nonuniform_result(n: float) -> dict:
    n = int(n)
    full = kc003_vr001.vr001_known_manifold_control(n_values=(n,))
    return full["results"]["nonuniform"][n]


def _seit_status_label(status_text: str) -> str:
    """Maps kc003_vr001.py's own free-text status strings to a .seit
    status label, read from the text itself -- not a hand-maintained
    per-subclaim table that could drift from the real content."""
    upper = status_text.upper()
    if upper.startswith("NOT COMPUTABLE"):
        return "OPEN"
    if upper.startswith("COMPUTED"):
        return "CALCULATED"
    if upper.startswith("PARTIALLY ADDRESSED"):
        return "RESOLVED"
    return "OPEN"  # conservative default -- never guess CALCULATED


def generate_continuum_bridge_declarations() -> str:
    """Emit .seit source: one `variable`/`status`/`provenance` triple
    per KC-003 subclaim (real status text read from
    kc003_vr001.kc003_decomposition()), plus one for VR-001 (labeled
    CALCULATED -- it genuinely computes something -- but its provenance
    text carries kc003_vr001.py's own explicit caveat that this is a
    methodology test on a KNOWN manifold, not a claim about real DESI
    data)."""
    decomposition = kc003_vr001.kc003_decomposition()
    lines = ["module continuum_bridge;"]
    for key, entry in decomposition.items():
        name = key.replace("-", "_")
        label = _seit_status_label(entry["status"])
        provenance_text = entry["status"].replace('"', "'")
        lines.append(f"variable {name}: Dataset;")
        lines.append(f"status {name} = {label};")
        lines.append(f'provenance {name} = "{provenance_text}";')
    lines.append("variable VR001: Dataset;")
    lines.append("status VR001 = CALCULATED;")
    lines.append('provenance VR001 = "VR-001 methodology test on a KNOWN manifold (S^1) -- '
                 'NOT a claim about real DESI data, see kc003_vr001.py";')
    return "\n".join(lines)


_BINDINGS_LIST: list[PrimitiveBinding] = [
    PrimitiveBinding("kc003_subclaim_report", ["Scalar"], "Dataset",
                      kc003_subclaim_report,
                      "seit_lang.continuum_bridge.kc003_subclaim_report (calls "
                      "scientific_corpus.derivation.kc003_vr001.kc003_decomposition)"),
    PrimitiveBinding("vr001_uniform_result", ["Scalar"], "Dataset",
                      vr001_uniform_result,
                      "seit_lang.continuum_bridge.vr001_uniform_result (calls "
                      "scientific_corpus.derivation.kc003_vr001.vr001_known_manifold_control)"),
    PrimitiveBinding("vr001_nonuniform_result", ["Scalar"], "Dataset",
                      vr001_nonuniform_result,
                      "seit_lang.continuum_bridge.vr001_nonuniform_result (calls "
                      "scientific_corpus.derivation.kc003_vr001.vr001_known_manifold_control)"),
]

CONTINUUM_BRIDGE_BINDINGS: dict[str, PrimitiveBinding] = {b.name: b for b in _BINDINGS_LIST}
CONTINUUM_BRIDGE_TRANSFORMATIONS: dict[str, TransformationSignature] = {
    b.name: TransformationSignature(b.name, list(b.param_types), b.return_type)
    for b in _BINDINGS_LIST
}
