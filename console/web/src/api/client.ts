/**
 * Thin fetch client. All requests go through the Vite dev-server proxy
 * (/api -> http://127.0.0.1:8000, see vite.config.ts) so there is no
 * hard-coded absolute origin here -- production builds should be
 * served behind a reverse proxy on the same rule.
 *
 * Phase 6 added the first mutating call, `api.runs.create()` (POST
 * /api/runs, triggers a real compiler.run_compiler.build_and_run()).
 * Phase 7 adds `api.hypotheses.create()`/`.transition()` -- both write
 * only to console_research/hypotheses.jsonl. Nothing in this client
 * (or anywhere else in the app) can set a node's status or write a
 * registry file directly.
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(`API error ${status}: ${detail}`);
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* response body was not JSON; keep statusText */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`);
  return handleResponse<T>(res);
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: "POST",
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  return handleResponse<T>(res);
}

export const api = {
  health: () => get<{ status: string; service: string; phase: number }>("/health"),
  state: () => get<import("./types").StateRollup>("/state"),
  mdcl: () => get<Record<string, unknown>>("/mdcl"),
  nodes: () => get<import("./types").NodeSummary[]>("/nodes"),
  node: (id: string) => get<import("./types").NodeDetail>(`/nodes/${encodeURIComponent(id)}`),
  frontier: () => get<import("./types").FrontierNode[]>("/frontier"),
  audits: () => get<import("./types").AuditResult[]>("/audits"),
  chainlink: () => get<import("./types").ChainlinkView>("/chainlink"),
  fc005: () => get<import("./types").Fc005Result>("/fc005"),
  runs: {
    list: () => get<import("./types").RunSnapshot[]>("/runs"),
    get: (runId: string) => get<import("./types").RunSnapshot>(`/runs/${encodeURIComponent(runId)}`),
    create: () => post<import("./types").RunSnapshot>("/runs"),
  },
  ledger: (limit = 50) => get<import("./types").LedgerEvent[]>(`/ledger?limit=${limit}`),
  hypotheses: {
    list: (filters?: { target_node_id?: string; status?: string }) => {
      const params = new URLSearchParams();
      if (filters?.target_node_id) params.set("target_node_id", filters.target_node_id);
      if (filters?.status) params.set("status", filters.status);
      const qs = params.toString();
      return get<import("./types").Hypothesis[]>(`/hypotheses${qs ? `?${qs}` : ""}`);
    },
    get: (id: string) => get<import("./types").HypothesisDetail>(`/hypotheses/${encodeURIComponent(id)}`),
    create: (req: {
      statement: string;
      target_node_id: string;
      dependencies?: string[];
      assumptions?: string[];
    }) => post<import("./types").HypothesisCreateResponse>("/hypotheses", req),
    transition: (id: string, req: { new_status: string; reason: string }) =>
      post<import("./types").Hypothesis>(`/hypotheses/${encodeURIComponent(id)}/transition`, req),
  },
  proofs: {
    list: () => get<import("./types").ProofRecordDetail[]>("/proofs"),
    get: (nodeId: string) => get<import("./types").ProofRecordDetail>(`/proofs/${encodeURIComponent(nodeId)}`),
  },
  falsifications: () => get<import("./types").FalsificationsResponse>("/falsifications"),
};
