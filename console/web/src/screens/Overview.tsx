import { StatCard } from "../components/StatCard";
import { useFrontier, useStateRollup } from "../api/queries";

const STATUS_ORDER = [
  "VERIFIED", "DERIVED", "CALCULATED", "CONDITIONAL", "PROPOSED", "OPEN", "FAIL", "FALSIFIED",
];

export function Overview() {
  const state = useStateRollup();
  const frontier = useFrontier();

  if (state.isLoading) return <p>Loading current theory state…</p>;
  if (state.isError) {
    return (
      <div className="error-panel">
        Could not load /api/state: {String(state.error)}. Is the API running
        (uvicorn console.api.main:app) and has `python3 -m compiler.run_compiler` been run at
        least once?
      </div>
    );
  }
  const s = state.data!;
  const closed = (s.by_status.VERIFIED ?? 0) + (s.by_status.DERIVED ?? 0)
    + (s.by_status.CALCULATED ?? 0) + (s.by_status.CONDITIONAL ?? 0);

  return (
    <div>
      <h1>Current Theory State</h1>
      <p className="section-note">
        Every number below is computed live from the actual registry files on this request --
        none of it is hard-coded (brief section VI).
      </p>

      <section className="stat-grid">
        <StatCard label="Mathematical closure" value={`${closed} / ${s.total_nodes}`} tone="neutral" />
        <StatCard label="Verified" value={s.by_status.VERIFIED ?? 0} tone="good" />
        <StatCard label="Derived" value={s.by_status.DERIVED ?? 0} tone="good" />
        <StatCard label="Calculated" value={s.by_status.CALCULATED ?? 0} tone="good" />
        <StatCard label="Conditional" value={s.by_status.CONDITIONAL ?? 0} tone="warn" />
        <StatCard label="Proposed" value={s.by_status.PROPOSED ?? 0} tone="neutral" />
        <StatCard label="Open" value={s.by_status.OPEN ?? 0} tone="neutral" />
        <StatCard label="Failed" value={s.by_status.FAIL ?? 0} tone="bad" />
        <StatCard label="Falsified" value={s.by_status.FALSIFIED ?? 0} tone="bad" />
        <StatCard
          label="Current frontier"
          value={frontier.data ? frontier.data.length : "…"}
          tone="neutral"
        />
        <StatCard
          label="Compiler status"
          value={s.all_audits_passed ? "PASS" : "FAIL"}
          tone={s.all_audits_passed ? "good" : "bad"}
        />
        <StatCard
          label="Terminal status"
          value={s.terminal_status ?? "UNKNOWN"}
          tone="neutral"
        />
      </section>

      <section>
        <h2>Status breakdown by kind</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Kind</th>
              <th>Count</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(s.by_kind).map(([kind, count]) => (
              <tr key={kind}>
                <td>{kind}</td>
                <td>{count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>Status distribution</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Count</th>
            </tr>
          </thead>
          <tbody>
            {STATUS_ORDER.filter((k) => s.by_status[k] !== undefined).map((k) => (
              <tr key={k}>
                <td>{k}</td>
                <td>{s.by_status[k]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <p className="section-note">
        No RUN-XXXX is active yet -- run orchestration (brief section XIV) has not been
        implemented (Phase 6+). This screen reflects the current on-disk registry state, most
        recently produced by a direct `python3 -m compiler.run_compiler` invocation, not by the
        console.
      </p>
    </div>
  );
}
