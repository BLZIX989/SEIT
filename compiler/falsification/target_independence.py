"""Target-independence firewall (spec section 26).

Scans registered IR nodes (and optionally raw text/code) for forbidden
downstream terms leaking into an upstream role. A forbidden term is only
permitted when the node's `role` is one of: validation, comparison,
falsification, observational_output.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FORBIDDEN_TERMS = [
    "SU(3)", "SU(2)", "U(1)", "G_SM", "3 generations", "three generations",
    "observed mass", "observed masses", "CKM", "PMNS", "observed coupling",
    "observed couplings", "DESI", "CMB", "Lambda_obs", "Λ_obs", "H_0", "H0",
    "Omega_m", "Ω_m", "Omega_Lambda", "Ω_Λ",
]

ALLOWED_ROLES = {"validation", "comparison", "falsification", "observational_output"}


@dataclass
class ContaminationFinding:
    node_id: str
    term: str
    role: str
    allowed: bool
    context: str = ""

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id, "term": self.term, "role": self.role,
            "allowed": self.allowed, "context": self.context,
        }


def _find_terms(text: str) -> list[str]:
    """Match forbidden terms as whole tokens, not as substrings of an
    unrelated English word (e.g. 'DESI' must not match inside
    'designed'). Alphabetic runs adjacent to the match are excluded via
    lookaround rather than \\b, since \\b fails at a ')'-then-space
    boundary (e.g. trailing \\b after 'SU(3)' would reject 'SU(3) x ...').
    """
    found = []
    for term in FORBIDDEN_TERMS:
        pattern = r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(term)
    return found


def scan_node(node_id: str, text_fields: list[str], role: str) -> list[ContaminationFinding]:
    """Scan a node's textual fields (action, derivation, lhs/rhs, etc.) for
    forbidden terms. `role` must be declared explicitly by the caller
    (default "upstream_construction" if not one of the allowed roles)."""
    findings = []
    blob = "\n".join(t for t in text_fields if t)
    for term in _find_terms(blob):
        allowed = role in ALLOWED_ROLES
        findings.append(ContaminationFinding(
            node_id=node_id, term=term, role=role, allowed=allowed,
            context=blob[:200],
        ))
    return findings


def scan_registries(registries) -> list[ContaminationFinding]:
    findings: list[ContaminationFinding] = []
    for obj in registries.objects:
        role = getattr(obj, "role", "upstream_construction")
        fields = [obj.type, obj.carrier if isinstance(obj.carrier, str) else "",
                  " ".join(obj.operations), " ".join(obj.relations),
                  " ".join(obj.constraints)]
        findings.extend(scan_node(obj.id, fields, role))
    for t in registries.transformations:
        role = getattr(t, "role", "upstream_construction")
        fields = [t.domain, t.codomain, t.action, t.proof]
        findings.extend(scan_node(t.id, fields, role))
    for eq in registries.equations:
        role = getattr(eq, "role", "upstream_construction")
        fields = [eq.lhs, eq.rhs, eq.domain, eq.derivation]
        findings.extend(scan_node(eq.id, fields, role))
    return findings


def scan_path(path: Path) -> list[ContaminationFinding]:
    """Best-effort static scan of a source/registry file for forbidden
    terms with no declared role (used by the self-audit as a coarse net
    over code, not a substitute for per-node role scanning)."""
    findings = []
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return findings
    for term in _find_terms(text):
        findings.append(ContaminationFinding(
            node_id=str(path), term=term, role="unscoped_file_scan", allowed=False,
            context="(file-level scan; see per-node scan for role context)",
        ))
    return findings
