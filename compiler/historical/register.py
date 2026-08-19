"""Historical T2 / NCG bridge registration (spec sections 33, 34).

This module registers PRIOR PROJECT CLAIMS found in the repository's
source documents (PDFs/DOCX predating this compiler) as historical nodes
with explicit provenance. It never wires them as upstream dependencies of
a fresh forward construction -- spec section 33: "Do NOT use them as
upstream selectors." Their `role` is declared "comparison" so the
target-independence firewall does not flag their necessarily-downstream
vocabulary (SU(3), SU(2), U(1), ...) as contamination, while still
refusing to promote any of them past PROPOSED without an executed
artifact in *this* compiler (spec section 2).

Where spec section 34 names specific obstruction artifacts
(abelian bridge obstruction, asymmetric-abelian obstruction, non-Abelian
commutant obstruction) that were not located anywhere in the repository
during the section-2 audit, this module registers them OPEN with an
explicit missing-artifact note rather than fabricating content (spec
section 39: report the exact obstruction and stop the branch).
"""
from __future__ import annotations

from compiler.core.ir import Object
from compiler.core.status import Status
from compiler.ir.registry import MDCLRegistries
from compiler.provenance.provenance import make_provenance

AUDITED_SOURCES = [
    "README.md",
    "DTC COMPILER.docx",
    "Functorial Gauge Unification v1.docx",
    "DTC_Formal_Structure.docx",
    "DTC Logic of Inquiry.docx",
    "DTC Metaphysics of Structure.docx",
    "DTC-RP-004_Forced_vs_Free.docx",
    "DTC_Rosetta_Stone_TOE_v2.docx",
    "Unified_Rosetta_Stone_TOE_v3.docx",
    "Universal_Rosetta_Ch1_Remainder.docx",
    "JOI Reformatted.docx",
    "Theory of Everything Equation Set.docx",
    "Unified Field Theory.docx",
    "geometric unification paper.docx",
    "Spectral Codex Volumes.docx",
    "Spectral Codex Volume I Genesis.pdf",
    "Spectral Codex Volume II Gravity.pdf",
    "Spectral Emergence Framework v2.pdf",
    "Spectral Emergence Information Theory.pdf",
    "Unified Spectral Codex.pdf",
    "SEIT Unified Derivation.pdf",
    "SEIT Unified Derivation v2.pdf",
    "SEIT v2.pdf",
    "Master Equation Codex.pdf",
    "MasterRosettaStone TOE Paper.pdf",
    "Constraint Core Brief.pdf",
    "Executive Summary.pdf",
    "Beyond the Theory of Everything.pdf",
    "Noncommutative Geometry and the Spectral Action_ Toward a Unified TOE.pdf",
    "Noncommutative Geometry and the Spectral Action_ Toward a Unified Theory.pdf",
]


def register_historical_nodes(registries: MDCLRegistries) -> list[str]:
    """Adds T2-HISTORICAL / T2-REPRODUCTION / T2-FORWARD-DERIVATION and the
    NCG bridge nodes to `registries`. Returns the list of node ids added.
    """
    added: list[str] = []

    t2_historical = Object(
        id="T2-HISTORICAL",
        type="historical_claim",
        status=Status.PROPOSED,
        role="comparison",
        carrier=(
            "Prose claim: G_physical = (1,3) x [SU(3) x SU(2) x U(1)] is asserted to be "
            "\"explicitly derived as the group of continuous automorphisms that preserve "
            "the invariant structural identity of the set A under local re-indexing\" "
            "(DTC COMPILER.docx, section 4). README.md separately states the historical "
            "claim Aut(O) x Spin(8) superset SU(3) x SU(2) x U(1) (octonion automorphism / "
            "Spin(8) route to the Standard Model gauge group)."
        ),
        assumptions=[
            "SOURCE CLAIM only: no executable derivation, proof object, or numerical "
            "artifact backing this claim was found anywhere in the repository during "
            "the spec-section-2 audit (searched: all .docx text, first pages of all "
            ".pdf files, README.md, and full git log).",
            "Per spec section 2, a document's own label (here, prose asserting "
            "\"explicitly derived\") is never promoted to VERIFIED/DERIVED on the "
            "strength of the label alone.",
        ],
    )
    t2_historical.provenance = make_provenance(
        source="DTC COMPILER.docx; README.md",
        object_id=t2_historical.id, status=Status.PROPOSED,
        verification={"artifact_found": False, "note": "prose assertion only"},
    )
    registries.objects.add_object(t2_historical)
    added.append(t2_historical.id)

    t2_reproduction = Object(
        id="T2-REPRODUCTION",
        type="reproduction_attempt",
        status=Status.OPEN,
        role="comparison",
        dependencies=[],  # deliberately NOT wired to T2-HISTORICAL: reproducing a claim
        carrier=(
            "Attempt to independently re-execute the T2-HISTORICAL automorphism-group "
            "construction inside this compiler (build Aut(O), build Spin(8) action, "
            "compute the invariant subgroup, compare to SU(3)xSU(2)xU(1) as a "
            "*comparison* target) has NOT been made in this build. This is out of scope "
            "for the initial compiler-construction phase (spec section 31/38: build the "
            "machine and the two initial executable tests first; gauge/matter engines "
            "activate only after the self-audit passes)."
        ),
        assumptions=["Not attempted; OPEN per spec section 5 (stop the branch, do not force closure)."],
    )
    t2_reproduction.provenance = make_provenance(
        source="this compiler build", object_id=t2_reproduction.id, status=Status.OPEN,
    )
    registries.objects.add_object(t2_reproduction)
    added.append(t2_reproduction.id)

    t2_forward = Object(
        id="T2-FORWARD-DERIVATION",
        type="forward_derivation_attempt",
        status=Status.OPEN,
        role="upstream_construction",
        dependencies=[],  # explicitly independent of T2-HISTORICAL (spec section 33)
        carrier=(
            "Forward derivation of a gauge structure from the upstream forward chain "
            "(Constraint -> Operator -> Spectrum -> Gauge) with no reference to any "
            "historically-targeted downstream gauge structure (see T2-HISTORICAL for "
            "the target this branch must NOT select toward). Not attempted: the Gauge "
            "engine is explicitly gated behind the self-audit in this build "
            "(spec section 41 final command)."
        ),
        assumptions=["Gauge engine not yet activated in this build; OPEN.",
                     "See T2-HISTORICAL for the downstream comparison target this node's "
                     "text and any future construction must remain independent of."],
    )
    t2_forward.provenance = make_provenance(
        source="this compiler build", object_id=t2_forward.id, status=Status.OPEN,
    )
    registries.objects.add_object(t2_forward)
    added.append(t2_forward.id)

    ncg_external = Object(
        id="NCG-BRIDGE-EXTERNAL-REFERENCE",
        type="external_literature_reference",
        status=Status.PROPOSED,
        role="comparison",
        carrier=(
            "Standard external result (Chamseddine-Connes spectral action on an "
            "almost-commutative spectral triple) summarized in "
            "'Noncommutative Geometry and the Spectral Action_ Toward a Unified TOE.pdf': "
            "\"when applied to an almost-commutative space (4D spacetime times a finite "
            "internal space), the Spectral Action Principle yields exactly the Standard "
            "Model coupled to gravity.\" This is third-party published NCG literature, "
            "not a SEIT-original derivation."
        ),
        assumptions=[
            "Registered as a comparison/validation target for a future forward "
            "reconstruction attempt, not as an upstream selector (spec section 34).",
        ],
    )
    ncg_external.provenance = make_provenance(
        source=(
            "Noncommutative Geometry and the Spectral Action_ Toward a Unified TOE.pdf; "
            "Noncommutative Geometry and the Spectral Action_ Toward a Unified Theory.pdf"
        ),
        object_id=ncg_external.id, status=Status.PROPOSED,
        verification={"artifact_found": False, "note": "literature review document, not executed derivation"},
    )
    registries.objects.add_object(ncg_external)
    added.append(ncg_external.id)

    obstruction_specs = [
        ("NCG-ABELIAN-BRIDGE-OBSTRUCTION", "abelian bridge obstruction"),
        ("NCG-ASYMMETRIC-ABELIAN-OBSTRUCTION", "asymmetric-abelian obstruction"),
        ("NCG-NONABELIAN-COMMUTANT-OBSTRUCTION", "non-Abelian commutant obstruction"),
    ]
    for node_id, name in obstruction_specs:
        obj = Object(
            id=node_id,
            type="missing_artifact",
            status=Status.OPEN,
            role="comparison",
            carrier=(
                f"Spec section 34 instructs this compiler to preserve the '{name}' "
                "theorem/proof artifact from prior seed->NCG experiments. No file in "
                "the repository (searched: all .docx converted to text, first pages of "
                "all .pdf files, README.md, git log of all prior commits) contains a "
                "theorem statement, proof, or computation matching this name."
            ),
            assumptions=[
                "STOP condition per spec section 39: missing dependency. Do not "
                "fabricate a proof artifact. If the underlying material exists outside "
                "this repository, it must be supplied and registered explicitly before "
                "this node can advance past OPEN.",
            ],
        )
        obj.provenance = make_provenance(
            source="compiler-build repository audit (spec section 2/36)",
            object_id=obj.id, status=Status.OPEN,
            verification={"artifact_found": False, "audited_sources": AUDITED_SOURCES},
        )
        registries.objects.add_object(obj)
        added.append(obj.id)

    dtc_circularity = Object(
        id="DTC-CIRCULARITY-OBSTRUCTION",
        type="self_acknowledged_obstruction",
        status=Status.CONDITIONAL,
        role="comparison",
        carrier=(
            "DTC_Formal_Structure.docx section 4.2 explicitly acknowledges: "
            "\"a derivation from C to R cannot be carried out, even in principle, if C "
            "has not been pinned down independently of the R it is meant to produce.\" "
            "This is a project-internal statement of exactly the circularity risk the "
            "target-independence firewall (spec section 26) is designed to catch: a "
            "downstream structure R must not silently define its own upstream "
            "selector C."
        ),
        assumptions=[
            "Registered verbatim as project-internal evidence that the circularity risk "
            "was recognized prior to this compiler build; not itself a derivation.",
        ],
    )
    dtc_circularity.provenance = make_provenance(
        source="DTC_Formal_Structure.docx (section 4.2)",
        object_id=dtc_circularity.id, status=Status.CONDITIONAL,
    )
    registries.objects.add_object(dtc_circularity)
    added.append(dtc_circularity.id)

    return added
