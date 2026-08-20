import { useState } from "react";
import { StatusBadge } from "../components/StatusBadge";
import { useRuns } from "../api/queries";
import type { RunSnapshot } from "../api/types";

/**
 * Real run history (Phase 6). Every row is a RunSnapshot actually
 * written to console_runs/{run_id}.json by
 * console/api/execution/executor.py after a POST /api/runs call --
 * there is no synthetic history here. Run-vs-run comparison (brief
 * section XXVI) is still Phase 10; this screen shows one run's full
 * diff on selection, not a multi-run comparison view yet.
 */
export function Runs() {
  const runs = useRuns();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const list = runs.data ?? [];
  const selected = list.find((r) => r.run_id === selectedId) ?? null;

  return (
    <div>
      <h1>Runs</h1>
      <p className="section-note">
        Every run below is a real, immutable RunSnapshot -- triggered via <code>POST /api/runs</code>{" "}
        from the Execution Console, which does nothing but invoke <code>compiler.run_compiler.build_and_run()</code>{" "}
        and record what actually changed on disk.
      </p>

      {runs.isLoading && <p>Loading run history…</p>}
      {list.length === 0 && !runs.isLoading && (
        <p className="section-note">No runs yet. Trigger one from the Execution Console.</p>
      )}

      {list.length > 0 && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Run ID</th><th>Started</th><th>Completed</th>
              <th>Terminal status</th><th>Outcome</th><th>Nodes changed</th>
            </tr>
          </thead>
          <tbody>
            {[...list].reverse().map((r) => (
              <tr
                key={r.run_id}
                className={r.run_id === selectedId ? "row--frontier" : undefined}
                style={{ cursor: "pointer" }}
                onClick={() => setSelectedId(r.run_id === selectedId ? null : r.run_id)}
              >
                <td><code>{r.run_id}</code></td>
                <td>{r.started_at}</td>
                <td>{r.completed_at ?? "—"}</td>
                <td>{r.terminal_status ?? "—"}</td>
                <td>{r.stopped_reason === "error"
                  ? <span className="tag" style={{ color: "var(--status-bad)" }}>ERROR</span>
                  : (r.stopped_reason ?? "…")}
                </td>
                <td>{r.diff ? r.diff.nodes_status_changed.length + r.diff.nodes_added.length : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selected && <RunDetail run={selected} />}
    </div>
  );
}

function RunDetail({ run }: { run: RunSnapshot }) {
  return (
    <div className="node-detail-panel" style={{ width: "auto", maxWidth: 760 }}>
      <div className="node-detail-panel__header">
        <h3><code>{run.run_id}</code></h3>
      </div>

      <table className="data-table">
        <tbody>
          <tr><td>Trigger</td><td>{run.trigger}</td></tr>
          <tr><td>Scope</td><td>{run.scope}</td></tr>
          <tr><td>Started</td><td>{run.started_at}</td></tr>
          <tr><td>Completed</td><td>{run.completed_at ?? "—"}</td></tr>
          <tr><td>Terminal status</td><td>{run.terminal_status ?? "—"}</td></tr>
          <tr><td>Stopped reason</td><td>{run.stopped_reason ?? "—"}</td></tr>
          <tr><td>Pre-state hash</td><td><code>{run.pre_state_hash.slice(0, 16)}…</code></td></tr>
          <tr><td>Post-state hash</td><td><code>{run.post_state_hash?.slice(0, 16) ?? "—"}</code></td></tr>
        </tbody>
      </table>

      {run.error && (
        <div className="error-panel" style={{ marginTop: 10 }}>{run.error}</div>
      )}

      {run.diff && (
        <>
          <h4>Nodes added ({run.diff.nodes_added.length})</h4>
          {run.diff.nodes_added.length === 0
            ? <p className="section-note">None.</p>
            : <ul className="node-ref-list">{run.diff.nodes_added.map((id) => <li key={id}><span className="tag">{id}</span></li>)}</ul>}

          <h4>Status changes ({run.diff.nodes_status_changed.length})</h4>
          {run.diff.nodes_status_changed.length === 0
            ? <p className="section-note">None -- no node's status changed in this run.</p>
            : (
              <table className="data-table">
                <thead><tr><th>Node</th><th>Old</th><th>New</th></tr></thead>
                <tbody>
                  {run.diff.nodes_status_changed.map((c) => (
                    <tr key={c.id}>
                      <td><code>{c.id}</code></td>
                      <td>{c.old_status ? <StatusBadge status={c.old_status} /> : "—"}</td>
                      <td><StatusBadge status={c.new_status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

          <h4>New falsifications ({run.diff.new_falsifications.length})</h4>
          <p className="section-note">{run.diff.new_falsifications.join(", ") || "None."}</p>

          <h4>New calculations ({run.diff.new_calculations.length})</h4>
          <p className="section-note">{run.diff.new_calculations.join(", ") || "None."}</p>

          <h4>Audit deltas ({run.diff.audit_deltas.length})</h4>
          <p className="section-note">{run.diff.audit_deltas.join(", ") || "No audit flipped pass/fail."}</p>
        </>
      )}
    </div>
  );
}
