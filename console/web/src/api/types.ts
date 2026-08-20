/**
 * TypeScript mirrors of console/api/models.py. Kept structurally
 * identical to the pydantic models on purpose -- these types describe
 * what the backend actually returns, they do not define a new,
 * independent frontend data model (per
 * UOC_RESEARCH_CONSOLE_ARCHITECTURE.md section 4.1's rule for the
 * Python side, applied the same way here).
 */

export type CanonicalStatus =
  | "VERIFIED"
  | "DERIVED"
  | "CALCULATED"
  | "CONDITIONAL"
  | "PROPOSED"
  | "OPEN"
  | "FAIL"
  | "FALSIFIED";

export type NodeKind = "Object" | "Transformation" | "Equation";

export interface Provenance {
  source: string;
  source_version: string;
  object_id: string;
  equation_id: string;
  dependency_ids: string[];
  transformation_id: string;
  calculation_id: string;
  execution_timestamp: string;
  git_commit: string;
  code_version: string;
  numerical_environment: Record<string, string>;
  status: string;
  verification: Record<string, unknown>;
}

export interface NodeSummary {
  id: string;
  kind: NodeKind;
  status: string;
  role: string;
  dependencies: string[];
  type?: string | null;
  domain?: string | null;
  codomain?: string | null;
}

export interface FalsificationMatch {
  record: Record<string, unknown>;
  match_confidence: "exact_id" | "prefix_match" | "substring_match";
}

export interface NodeDetail {
  id: string;
  kind: NodeKind;
  status: string;
  role: string;
  raw: Record<string, unknown>;
  dependencies: string[];
  dependents: string[];
  provenance: Provenance | null;
  proofs: Record<string, unknown>[];
  calculations: Record<string, unknown>[];
  falsifications: FalsificationMatch[];
  superseding_nodes: string[];
  superseding_nodes_note: string;
}

export interface AuditResult {
  name: string;
  passed: boolean;
  issues: string[];
  details: Record<string, unknown>;
}

export interface StateRollup {
  total_nodes: number;
  by_status: Record<string, number>;
  by_kind: Record<string, number>;
  terminal_status: string | null;
  all_audits_passed: boolean;
  audits: AuditResult[];
  fc005_terminal_status: string | null;
  frontier_size: number;
  generated_from: Record<string, string>;
}

export interface FrontierNode {
  id: string;
  kind: NodeKind;
  status: string;
  unresolved_dependency_count: number;
  resolved_dependencies: string[];
  downstream_unlock_count: number;
}

export interface ChainlinkArrow {
  from_id: string;
  to_id: string;
  from_symbol: string;
  to_symbol: string;
  status: string;
  der_id: string | null;
  der_id_note: string;
  proof: Record<string, unknown>[];
  dependencies: string[];
  assumptions: string[];
  calculations: Record<string, unknown>[];
  failures: FalsificationMatch[];
  open_obligations: string[];
  literature: Record<string, unknown>[];
  literature_note: string;
  execution_status: "EXECUTED" | "NOT_IMPLEMENTED";
}

export interface ChainlinkView {
  arrows: ChainlinkArrow[];
  note: string;
}

export interface Fc005Result {
  terminal_status: string | null;
  all_self_audits_passed?: boolean;
  [key: string]: unknown;
}
