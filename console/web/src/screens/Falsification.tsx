import { useState } from "react";
import { NotImplemented } from "../components/NotImplemented";
import { useFalsifications } from "../api/queries";

/**
 * Falsification Workspace (Phase 8). Every record below is real,
 * verbatim falsification_registry.json content -- including failed
 * ones, which are never filtered out ("failed tests remain permanently
 * attached"). The protocol reference panel lists the compiler's real,
 * available falsification protocol types (pulled live via `inspect`
 * from compiler/falsification/protocols.py) -- it is a reference, not
 * a menu of runnable actions: each protocol needs real per-node math
 * wired in by hand, and no generic runner exists.
 */
export function Falsification() {
  const data = useFalsifications();
  const [protocolFilter, setProtocolFilter] = useState("");
  const [outcomeFilter, setOutcomeFilter] = useState<"" | "passed" | "failed">("");

  const records = (data.data?.records ?? []) as Array<Record<string, unknown>>;
  const filtered = records.filter((r) => {
    if (protocolFilter && r.protocol !== protocolFilter) return false;
    if (outcomeFilter === "passed" && r.passed !== true) return false;
    if (outcomeFilter === "failed" && r.passed !== false) return false;
    return true;
  });
  const protocolNames = Array.from(new Set(records.map((r) => String(r.protocol))));

  return (
    <div>
      <h1>Falsification</h1>
      <p className="section-note">
        &ldquo;WHAT WOULD FALSIFY THIS?&rdquo; -- every executed test below is real, from{" "}
        <code>falsification_registry.json</code>. Failed tests are never hidden or removed.
      </p>

      <h2>Available protocols (reference)</h2>
      <p className="section-note">
        The compiler's real falsification protocol types, read live from
        <code> compiler/falsification/protocols.py</code>. This is a reference list, not a
        &ldquo;run a new test&rdquo; menu -- see the note at the bottom of this page.
      </p>
      {data.data && (
        <table className="data-table">
          <thead><tr><th>Protocol</th><th>Summary</th></tr></thead>
          <tbody>
            {data.data.protocols.map((p) => (
              <tr key={p.name}><td><code>{p.name}</code></td><td>{p.summary}</td></tr>
            ))}
          </tbody>
        </table>
      )}

      <h2>Executed tests ({records.length})</h2>
      <div className="filter-group" style={{ marginBottom: 10 }}>
        <span className="filter-group__label">Protocol</span>
        <select value={protocolFilter} onChange={(e) => setProtocolFilter(e.target.value)}>
          <option value="">All</option>
          {protocolNames.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <span className="filter-group__label">Outcome</span>
        <select value={outcomeFilter} onChange={(e) => setOutcomeFilter(e.target.value as "" | "passed" | "failed")}>
          <option value="">All</option>
          <option value="passed">Passed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {records.length === 0 && !data.isLoading && <p className="section-note">No falsification tests recorded yet.</p>}

      {filtered.length > 0 && (
        <table className="data-table">
          <thead><tr><th>ID</th><th>Protocol</th><th>Target</th><th>Outcome</th><th>Detail</th></tr></thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={String(r.id)}>
                <td><code>{String(r.id)}</code></td>
                <td>{String(r.protocol)}</td>
                <td>{String(r.target)}</td>
                <td>{r.passed
                  ? <span className="tag tag--executed">passed</span>
                  : <span className="tag" style={{ color: "var(--status-bad)", borderColor: "var(--status-bad)" }}>failed</span>}
                </td>
                <td>{String(r.detail)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <NotImplemented
        feature="Propose and run a new falsification test against an arbitrary node"
        reason="Each protocol above takes real Python callables/candidate data specific to a
          node's actual math (e.g. a graph construction, a set of representations to compare) --
          there is no generic way to parameterize that from a web form without either faking the
          math or hand-wiring a backend per node. Every test on this page already ran for real;
          none is simulated here."
      />
    </div>
  );
}
