/**
 * Thin fetch client. All requests go through the Vite dev-server proxy
 * (/api -> http://127.0.0.1:8000, see vite.config.ts) so there is no
 * hard-coded absolute origin here -- production builds should be
 * served behind a reverse proxy on the same rule.
 *
 * This client only ever issues GET requests in Phase 3, matching the
 * backend's Phase 2 read-only scope. There is intentionally no
 * post()/mutate() helper here yet -- adding one is a Phase 6 decision,
 * not an accidental side effect of scaffolding the client.
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(`API error ${status}: ${detail}`);
  }
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`);
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
};
