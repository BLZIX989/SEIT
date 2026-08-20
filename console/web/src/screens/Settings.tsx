import { useHealth } from "../api/queries";

export function Settings() {
  const health = useHealth();

  return (
    <div>
      <h1>Settings</h1>
      <table className="data-table">
        <tbody>
          <tr><td>API base path</td><td><code>/api</code> (proxied to the FastAPI backend by the Vite dev server; see vite.config.ts)</td></tr>
          <tr><td>API status</td><td>{health.isLoading ? "checking…" : health.isError ? "unreachable" : "reachable"}</td></tr>
          <tr><td>API phase</td><td>{health.data?.phase ?? "…"}</td></tr>
          <tr><td>Console version</td><td>0.1.0-phase3</td></tr>
        </tbody>
      </table>
      <p className="section-note">
        No user-configurable settings exist yet -- there is no auth, no per-user preference store,
        and no run-policy configuration UI (that belongs with the Runs screen once run
        orchestration exists in Phase 6). This screen is a status page for now.
      </p>
    </div>
  );
}
