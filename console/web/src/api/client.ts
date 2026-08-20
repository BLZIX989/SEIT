/**
 * Thin fetch client. All requests go through the Vite dev-server proxy
 * (/api -> http://127.0.0.1:8000, see vite.config.ts) so there is no
 * hard-coded absolute origin here -- production builds should be
 * served behind a reverse proxy on the same rule.
 *
 * Phase 6 adds the one and only mutating call: `api.runs.create()`,
 * a POST to /api/runs. It exists to trigger a real
 * `compiler.run_compiler.build_and_run()` on the backend -- nothing in
 * this client (or anywhere else in the app) can set a node's status or
 * write a registry file directly.
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

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`, { method: "POST" });
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
};
