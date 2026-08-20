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

export interface CircularDependencyCheck {
  is_circular: boolean;
  cycle_path: string[] | null;
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
  circular_dependency: CircularDependencyCheck;
}

export interface ProofRecordDetail {
  id: string;
  transformation_id: string;
  statement: string;
  method: string;
  status: string;
  preconditions: string[];
  postconditions: string[];
  assumptions: string[];
  dependencies: string[];
  open_obligations: string[];
  circular_dependency: CircularDependencyCheck;
}

export interface ProtocolReference {
  name: string;
  summary: string;
}

export interface FalsificationsResponse {
  records: Record<string, unknown>[];
  protocols: ProtocolReference[];
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
  historical_failure_rate: number | null;
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

export interface NodeStatusChange {
  id: string;
  old_status: string | null;
  new_status: string;
}

export interface RunDiff {
  nodes_added: string[];
  nodes_status_changed: NodeStatusChange[];
  nodes_unchanged: number;
  new_falsifications: string[];
  new_calculations: string[];
  audit_deltas: string[];
}

export type StoppedReason =
  | "completed"
  | "no_admissible_frontier"
  | "dependency_failed"
  | "proof_obligation_unsatisfied"
  | "external_dependency_unavailable"
  | "resource_limit"
  | "user_stopped"
  | "error";

export interface RunSnapshot {
  run_id: string;
  started_at: string;
  completed_at: string | null;
  trigger: "full_rebuild";
  scope: "full_rebuild";
  target_node_ids: string[];
  pre_state_hash: string;
  post_state_hash: string | null;
  diff: RunDiff | null;
  test_suite_result: Record<string, unknown> | null;
  self_audit_result: AuditResult[] | null;
  terminal_status: string | null;
  stopped_reason: StoppedReason | null;
  error: string | null;
}

export interface LedgerEvent {
  event_id: string;
  timestamp: string;
  run_id: string | null;
  actor: "system" | "user" | "research_engine";
  node_id: string | null;
  action:
    | "RUN_STARTED" | "NODE_SELECTED" | "LITERATURE_SEARCH" | "SOURCE_ACQUIRED"
    | "CANDIDATE_CREATED" | "DERIVATION_EXECUTED" | "PROOF_ATTEMPTED"
    | "TEST_EXECUTED" | "FALSIFICATION" | "PROMOTION" | "REJECTION"
    | "SUPERSESSION" | "AUDIT_COMPLETED" | "RUN_COMPLETED";
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  status: string;
  provenance: Record<string, unknown>;
  content_hash: string | null;
}

export type HypothesisStatus =
  | "PROPOSED" | "TESTING" | "SUPPORTED" | "DERIVED" | "VERIFIED"
  | "REJECTED" | "FALSIFIED" | "SUPERSEDED" | "BLOCKED";

export interface EvidenceRef {
  description: string;
  kind: "ledger_event" | "run" | "external" | "other";
  ref_id: string | null;
}

export interface TestRef {
  description: string;
  result: "pass" | "fail" | "pending" | null;
}

export interface Hypothesis {
  id: string;
  statement: string;
  target_node_id: string;
  dependencies: string[];
  assumptions: string[];
  evidence: EvidenceRef[];
  tests: TestRef[];
  status: HypothesisStatus;
  created_at: string;
  updated_at: string;
  provenance: Record<string, unknown>;
  superseded_by: string | null;
}

export interface PossibleDuplicate {
  id: string;
  statement: string;
  status: string;
  match_confidence: "exact_normalized_match" | "word_overlap";
  similarity: number;
}

export interface HypothesisCreateResponse {
  hypothesis: Hypothesis;
  possible_duplicates: PossibleDuplicate[];
}

export interface HypothesisDetail {
  current: Hypothesis;
  history: Hypothesis[];
}
