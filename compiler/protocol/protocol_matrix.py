"""Crosswalk engine for the peer-review protocol taxonomy
(compiler/protocol/protocol_taxonomy.py) against this repository's REAL,
already-executed canonical registries.

Governing rule, matching this whole project's discipline: a protocol's
computed status here is read directly off a real Object/Transformation/
Chainlink/self-audit-result/Protocol/on-disk-document that this exact
compiler run produced -- never asserted, never inferred from prose, and
never fuzzy-matched. `_CORRESPONDENCES` is an explicit, hand-built,
one-protocol-id-to-one-real-artifact dict (same discipline as
derivation_chainlinks.py's `_FALSIFICATION_ID_PREFIXES`): if a protocol
ID is not a key in it, this crosswalk found NO real artifact backing it
in the canonical MDCL registries, and it is reported as exactly that --
`NO_CORRESPONDING_ARTIFACT` -- not silently omitted and not guessed at.

SCOPE, stated explicitly rather than left implicit: this crosswalk reads
ONLY the registries `python3 -m compiler.run_compiler` itself produces
(status_matrix / object_registry / chainlink_registry / self_audit_report
/ protocol_registry). Real work exists elsewhere in this repository
(scientific_corpus/derivation/*.py, seit_lang/*.py) that is NOT registered
into these canonical registries; where that is true for a specific
protocol, the correspondence entry's `note` says so explicitly rather
than reaching outside this run's own registries to manufacture a
correspondence a reviewer could not verify from the same artifacts this
compiler run just produced.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from compiler.ir.registry import MDCLRegistries
from compiler.protocol.protocol_taxonomy import LAYER_NAMES, LAYER_REVIEW_QUESTION, TAXONOMY
from compiler.protocol.registry import ChainlinkRegistry, ProtocolRegistry

NO_ARTIFACT = "NO_CORRESPONDING_ARTIFACT"


@dataclass
class Correspondence:
    kind: str            # "object" | "equation" | "chainlink" | "chainlink_falsification"
                          # | "audit" | "document" | "callable" | "protocol"
    ref: str
    note: str = ""


# Explicit, hand-checked crosswalk. Every entry below was verified against
# this repository's real registries during this session's audit -- see
# the conversation record for the per-entry reasoning. Absence from this
# dict is itself the honest finding for that protocol ID.
_CORRESPONDENCES: dict[str, Correspondence] = {
    # I. Meta-Compiler / Governance
    "MC-001": Correspondence("document", "FORWARD_MDCL_COMPILER_SPEC.md"),
    "MC-002": Correspondence("document", "master_mdcl.json"),
    "MC-003": Correspondence("audit", "dependency_audit",
                              "topological-order confirmation over the real dependency DAG"),
    "MC-004": Correspondence("document", "object_registry.json",
                              "one of several universal registries this run produced; "
                              "see also transformation_registry.json, equation_registry.json"),
    "MC-005": Correspondence("audit", "provenance_audit"),
    "MC-006": Correspondence("audit", "status_audit"),
    "MC-007": Correspondence("document", "chainlink_registry.json",
                              "the Chainlink layer plays the PDG role: dependencies + proof_status "
                              "per edge, status always computed from a real Transformation/Object"),
    # MC-008: no entry -- only duplicate-id guarding exists (Registry.add),
    # not a canonical-normal-form / one-representation-per-object check.
    "MC-009": Correspondence("audit", "numerical_reproducibility_audit"),
    "MC-010": Correspondence("protocol", "PROTOCOL-STRUCTURAL-FALSIFICATION"),

    # II. Primitive-Recovery
    # PR-001: no entry -- the graph G is directly postulated (spec section 31),
    # not derived via any primitive-extraction process (see
    # PROTOCOL-GRAPH-SPECTRAL-DERIVATION's own registered assumption).
    "PR-002": Correspondence("callable", "compiler.falsification.protocols:structural_elimination_protocol"),
    "PR-003": Correspondence("callable", "compiler.falsification.protocols:representation_invariance_test"),
    "PR-004": Correspondence("callable", "compiler.falsification.protocols:mathematical_invariance_test"),
    # PR-005..PR-008: no entry -- nothing tests mutual primitive
    # reducibility, certifies irreducibility, reconstructs from primitives,
    # or compresses a domain ontology into primitive grammar.

    # III. Organizational Grammar -- the section-6 dependency TEMPLATE
    # (compiler/ir/forward_chain.py), registered OPEN by construction: a
    # template is not a proof, and none of these has an executed
    # transformation attached.
    "OG-001": Correspondence("object", "DISTINCTION"),
    "OG-002": Correspondence("object", "TRANSFORMATION-NODE"),
    "OG-003": Correspondence("object", "CONSTRAINT"),
    "OG-004": Correspondence("object", "RELATION",
                              "R(Omega_i,Omega_j) is the template's composition point between "
                              "Distinction and Transformation"),
    # OG-005..007 (Psi organizational state/dynamics/fixed-point): no entry
    # -- no Psi object exists anywhere in the template or the registries.
    "OG-008": Correspondence("object", "PERSISTENCE-NODE"),
    # OG-009..012: no entry.

    # IV. Mathematical Recovery -- the REAL executed graph/spectral chain.
    "MR-003": Correspondence("object", "GRAPH-G-SEED"),
    "MR-006": Correspondence("chainlink", "CL-G-TO-L"),
    "MR-007": Correspondence("chainlink", "CL-L-TO-SPECL"),
    "MR-008": Correspondence("chainlink", "CL-L-TO-SPECL",
                              "eigenmodes (lambda_n,phi_n) are the content of the spectrum "
                              "computed here"),
    "MR-009": Correspondence("chainlink", "CL-HEATFLOW-TO-KERNEL",
                              "the t->inf kernel projector IS this system's persistence sector"),
    "MR-010": Correspondence("chainlink", "CL-SPECL-TO-DIFFUSION"),
    "MR-011": Correspondence("chainlink", "CL-DIFFUSION-TO-METRIC",
                              "CONDITIONAL: depends on a free, non-unique diffusion-time parameter"),
    "MR-012": Correspondence("chainlink", "CL-METRIC-TO-CONNECTION",
                              "OPEN: the honest frontier -- no admissible connection construction "
                              "from a non-unique metric candidate is registered"),
    "MR-013": Correspondence("chainlink", "CL-OPERATOR-TO-CURVATURE-DISCRETE",
                              "Ollivier-Ricci DISCRETE graph curvature -- a real, independent route, "
                              "NOT the continuum Riemann tensor R^rho_sigmamunu this protocol names; "
                              "see that chainlink's own note that it does not resolve CL-METRIC-TO-CONNECTION"),
    # MR-014..016 (Ricci/scalar-curvature/Einstein-tensor): no entry --
    # not separately recovered from this project's own primitives; the
    # Lichnerowicz/Seeley-DeWitt work (CL-CONTROL-TO-LICHNEROWICZ-GRAVITY)
    # uses an EXTERNALLY SPECIFIED R on a control manifold (round S^2/S^3),
    # not one derived from G->L->metric.
    "MR-017": Correspondence("object", "VARIATIONAL-NODE"),
    # MR-018: no entry.

    # V. Statistical / Information-Geometric
    "SG-011": Correspondence("object", "FISHER-STATISTICAL-FAMILY"),
    "SG-012": Correspondence("equation", "EQ-FC005-FISHER-LORENTZIAN-OBSTRUCTION",
                              "FALSIFIED: the Fisher-Rao route was tried and rejected with a "
                              "counterexample, not silently dropped"),
    # SG-001..010, SG-013..015: no entry.

    # VI. Physical Recovery
    "PH-009": Correspondence("object", "THERMODYNAMICS-NODE"),
    # PH-001..008, PH-010..013: no entry.

    # VII. Quantum Recovery
    "QR-004": Correspondence("object", "DOUBLED-HILBERT-SPACE-H_F-PRIME",
                              "a FINITE-dimensional Hilbert space for a candidate spectral triple, "
                              "not a general quantum-mechanical Hilbert space"),
    "QR-012": Correspondence("object", "FINITE-DIRAC-D_B",
                              "a FINITE, discrete, graph-based Dirac-TYPE operator "
                              "(self-adjoint, grading-anticommuting), not the continuum Dirac "
                              "equation for spinor fields on spacetime"),
    # QR-001..003, QR-005..011, QR-013, QR-014: no entry.

    # VIII. Gauge / Representation / Matter
    "GM-001": Correspondence("object", "GAUGE-NODE"),
    "GM-002": Correspondence("object", "H4-DIRECT-PRODUCT-CLAIM-UNCONSTRUCTED",
                              "necessary rank/dimension conditions checked; no explicit embedding "
                              "constructed"),
    "GM-003": Correspondence("object", "MATTER-NODE"),
    "GM-005": Correspondence("object", "OMEGA_B-COUPLED-RECOVERY",
                              "NCG inner-fluctuation curvature for a finite candidate with ONE "
                              "generator, not the general non-abelian field-strength tensor F_munu "
                              "of a continuum gauge theory"),
    "GM-007": Correspondence("equation", "EQ-H4-G2-TRIALITY-INTERSECTION-CLAIM",
                              "FALSIFIED: the G2/Spin(8) triality-intersection route to "
                              "SU(3)xSU(2)xU(1) specifically, rank obstruction"),
    # GM-004, GM-006, GM-008..013: no entry. GM-010 (mass generation) has
    # real work OUTSIDE the canonical registries this crosswalk reads --
    # see scientific_corpus/derivation/mass_spectrum.py (mass spectrum
    # misses real tau/mu masses by 1-2 orders of magnitude, honestly
    # reported in DERIVATION_FRONTIER.md) -- not registered as a canonical
    # MDCL Object, so it cannot be cited here as a verifiable artifact of
    # THIS run.

    # IX. Spectral / Constants
    "SC-001": Correspondence("chainlink", "CL-L-TO-SPECL"),
    "SC-012": Correspondence("chainlink_falsification", "CL-L-TO-SPECL"),
    # SC-002 (eigenvalue physical interpretation) and SC-003
    # (ground-state-subtraction uniqueness) and SC-011 (spectral-to-physical
    # map): NO ENTRY -- these are the exact open questions flagged earlier
    # in this project's own history ("why does lambda_n have the required
    # physical interpretation?", "why is lambda_n-lambda_0 uniquely
    # required?") and remain genuinely unresolved; reported here as
    # NO_CORRESPONDING_ARTIFACT rather than buried in a derivation.
    # SC-004..010: no entry.

    # X. Cosmological Closure
    "CO-008": Correspondence("chainlink", "CL-OPERATOR-TO-CONTINUUM-DESI",
                              "FAIL: DESI graph-Laplacian continuum-limit attempt"),
    "CO-010": Correspondence("object", "CONTINUUM-LIMIT-L-DESI"),
    # CO-001..007, CO-009, CO-011, CO-012: no entry.

    # XI. Quantum-Gravity / Unification Closure
    "UG-003": Correspondence("object", "FINITE-SPECTRAL-TRIPLE-CERTIFICATION",
                              "FAIL for the original candidate; see the coupled-recovery "
                              "candidate (OMEGA_B-COUPLED-RECOVERY) for the one construction "
                              "that does pass"),
    # UG-001,002,004..012: no entry. UG-012 (Unification Closure Test) in
    # particular has NO real artifact anywhere in this corpus -- this is
    # exactly the top-level gate that does not yet exist.

    # XII. Empirical Validation
    "EV-007": Correspondence("equation", "EQ-H4-G2-TRIALITY-INTERSECTION-CLAIM"),
    "EV-008": Correspondence("object", "CONTINUUM-LIMIT-L-DESI"),
    "EV-013": Correspondence("audit", "numerical_reproducibility_audit",
                              "INTERNAL bitwise re-run comparison, not independent-group "
                              "reproduction"),
    "EV-015": Correspondence("audit", "leakage_control_audit"),
    # EV-001..006, EV-009..012, EV-014: no entry.

    # XIII. Closure Gate
    # UCC-001: no entry, deliberately -- there is no single audit or
    # artifact anywhere in this corpus that computes T=>R=>P=>E end to
    # end. This is the single most consequential absence this crosswalk
    # surfaces.
}


@dataclass
class ProtocolMatrixEntry:
    protocol_id: str
    layer: str
    layer_name: str
    family_or_target: str
    description: str
    computed_status: str
    evidence: str
    correspondence_kind: str | None
    correspondence_ref: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_id": self.protocol_id, "layer": self.layer, "layer_name": self.layer_name,
            "family_or_target": self.family_or_target, "description": self.description,
            "computed_status": self.computed_status, "evidence": self.evidence,
            "correspondence_kind": self.correspondence_kind, "correspondence_ref": self.correspondence_ref,
        }


def _resolve(corr: Correspondence, registries: MDCLRegistries, chainlinks: ChainlinkRegistry,
             protocols: ProtocolRegistry, audit_by_name: dict[str, Any], repo_root: Path) -> tuple[str, str]:
    if corr.kind == "object":
        if corr.ref not in registries.objects:
            return "REFERENCE_ERROR", f"object '{corr.ref}' not found in this run's registries"
        obj = registries.objects.get(corr.ref)
        status = obj.status.value if hasattr(obj.status, "value") else str(obj.status)
        ev = f"object {corr.ref}: status={status}; carrier={obj.carrier[:160]!r}"
        return status, (ev + (f" -- {corr.note}" if corr.note else ""))
    if corr.kind == "equation":
        if corr.ref not in registries.equations:
            return "REFERENCE_ERROR", f"equation '{corr.ref}' not found in this run's registries"
        eq = registries.equations.get(corr.ref)
        status = eq.status.value if hasattr(eq.status, "value") else str(eq.status)
        ev = f"equation {corr.ref}: status={status}"
        return status, (ev + (f" -- {corr.note}" if corr.note else ""))
    if corr.kind == "chainlink":
        if corr.ref not in chainlinks:
            return "REFERENCE_ERROR", f"chainlink '{corr.ref}' not found in this run's chainlink registry"
        link = chainlinks.get(corr.ref)
        ev = f"chainlink {corr.ref}: status={link.status}; statement={link.mathematical_statement[:160]!r}"
        return link.status, (ev + (f" -- {corr.note}" if corr.note else ""))
    if corr.kind == "chainlink_falsification":
        if corr.ref not in chainlinks:
            return "REFERENCE_ERROR", f"chainlink '{corr.ref}' not found in this run's chainlink registry"
        link = chainlinks.get(corr.ref)
        ev = f"chainlink {corr.ref}: falsification_status={link.falsification_status}"
        return link.falsification_status, (ev + (f" -- {corr.note}" if corr.note else ""))
    if corr.kind == "audit":
        if corr.ref not in audit_by_name:
            return "REFERENCE_ERROR", f"self-audit '{corr.ref}' not found in this run's audit results"
        a = audit_by_name[corr.ref]
        status = "PASS" if a.passed else "FAIL"
        ev = f"self_audit {corr.ref}: passed={a.passed}, {len(a.issues)} issues"
        return status, (ev + (f" -- {corr.note}" if corr.note else ""))
    if corr.kind == "protocol":
        if corr.ref not in protocols:
            return "REFERENCE_ERROR", f"protocol '{corr.ref}' not found in this run's protocol registry"
        return "REGISTERED", f"formally registered as {corr.ref} in protocol_registry.json"
    if corr.kind == "document":
        exists = (repo_root / corr.ref).exists()
        status = "DOCUMENT_EXISTS" if exists else "DOCUMENT_MISSING"
        ev = f"{corr.ref}: {'found' if exists else 'NOT found'} at repository root"
        return status, (ev + (f" -- {corr.note}" if corr.note else ""))
    if corr.kind == "callable":
        module_path, _, func_name = corr.ref.partition(":")
        try:
            mod = importlib.import_module(module_path)
            ok = hasattr(mod, func_name) and callable(getattr(mod, func_name))
        except ImportError:
            ok = False
        status = "CODE_EXISTS_AND_CALLABLE" if ok else "CODE_MISSING"
        ev = f"{corr.ref}: {'importable and callable' if ok else 'NOT importable/callable'}"
        return status, (ev + (f" -- {corr.note}" if corr.note else ""))
    return "REFERENCE_ERROR", f"unknown correspondence kind '{corr.kind}'"


def build_protocol_matrix(
    registries: MDCLRegistries, chainlinks: ChainlinkRegistry, protocols: ProtocolRegistry,
    audit_results: list, repo_root: Path,
) -> list[ProtocolMatrixEntry]:
    """Computes the full protocol matrix. Every status is read from a real
    artifact this exact run produced (see `_resolve`); absent a mapping in
    `_CORRESPONDENCES`, the honest result is NO_CORRESPONDING_ARTIFACT."""
    audit_by_name = {a.name: a for a in audit_results}
    entries: list[ProtocolMatrixEntry] = []
    for taxon in TAXONOMY:
        corr = _CORRESPONDENCES.get(taxon.protocol_id)
        if corr is None:
            entries.append(ProtocolMatrixEntry(
                protocol_id=taxon.protocol_id, layer=taxon.layer,
                layer_name=LAYER_NAMES[taxon.layer], family_or_target=taxon.family_or_target,
                description=taxon.description, computed_status=NO_ARTIFACT,
                evidence="no real artifact in this repository's canonical MDCL registries "
                         "addresses this protocol",
                correspondence_kind=None, correspondence_ref=None,
            ))
            continue
        status, evidence = _resolve(corr, registries, chainlinks, protocols, audit_by_name, repo_root)
        entries.append(ProtocolMatrixEntry(
            protocol_id=taxon.protocol_id, layer=taxon.layer, layer_name=LAYER_NAMES[taxon.layer],
            family_or_target=taxon.family_or_target, description=taxon.description,
            computed_status=status, evidence=evidence,
            correspondence_kind=corr.kind, correspondence_ref=corr.ref,
        ))
    return entries


def layer_summary(entries: list[ProtocolMatrixEntry]) -> list[dict]:
    """Per-layer rollup: how many protocols in this layer have ANY real
    backing (any status other than NO_CORRESPONDING_ARTIFACT/
    REFERENCE_ERROR) vs. how many do not."""
    by_layer: dict[str, list[ProtocolMatrixEntry]] = {}
    for e in entries:
        by_layer.setdefault(e.layer, []).append(e)
    out = []
    # Preserve the taxonomy's own layer ordering (I..XIII).
    for layer in LAYER_NAMES:
        group = by_layer.get(layer)
        if not group:
            continue
        n_total = len(group)
        n_backed = sum(1 for e in group if e.computed_status not in (NO_ARTIFACT, "REFERENCE_ERROR"))
        question, requested_status = LAYER_REVIEW_QUESTION.get(layer, ("", ""))
        out.append({
            "layer": layer, "layer_name": LAYER_NAMES[layer],
            "reviewer_question": question, "requested_status": requested_status,
            "n_protocols_total": n_total, "n_with_real_backing": n_backed,
            "n_no_corresponding_artifact": n_total - n_backed,
        })
    return out
