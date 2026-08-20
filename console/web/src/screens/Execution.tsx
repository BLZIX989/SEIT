import { Link } from "react-router-dom";
import { useAudits, useCreateRun, useLedger, useStateRollup } from "../api/queries";
import { NotImplemented } from "../components/NotImplemented";

const STAGES = [
  { id: "01", label: "LOAD" },
  { id: "02", label: "CANONICALIZE" },
  { id: "03", label: "RESOLVE" },
  { id: "04", label: "DEPENDENCY" },
  { id: "05", label: "COMPILE" },
  { id: "06", label: "EXECUTE" },
  { id: "07", label: "PROVE" },
  { id: "08", label: "FALSIFY" },
  { id: "09", label: "AUDIT" },
  { id: "10", label: "PROMOTE" },
  { id: "11", label: "PUBLISH" },
];

/**
 * Brief section XIII's build-ladder view, plus (Phase 6) the real
 * RUN THEORY SEARCH trigger: POST /api/runs, which invokes
 * compiler.run_compiler.build_and_run() and nothing else. The ladder
 * itself still shows only stage 09 (AUDIT) as real: build_and_run() is
 * one atomic function with no discrete per-stage events to report, so
 * stages 01-08/10-11 stay NOT IMPLEMENTED rather than faking a
 * stage-by-stage progress bar around a run that is actually atomic.
 */
export function Execution() {
  const audits = useAudits();
  const state = useStateRollup();
  const ledger = useLedger(20);
  const createRun = useCreateRun();

  return (
    <div>
      <h1>Execution Console</h1>

      <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "12px 0 20px" }}>
        <button
          className="link-button"
          style={{ fontSize: 13, padding: "8px 16px", fontWeight: 700 }}
          disabled={createRun.isPending}
          onClick={() => createRun.mutate()}
        >
          {createRun.isPending ? "RUNNING…" : "[ RUN THEORY SEARCH ]"}
        </button>
        <span className="section-note" style={{ margin: 0 }}>
          Today this triggers a full compiler rebuild (<code>POST /api/runs</code>) -- not yet the
          frontier-targeted selection → research → candidate generation cycle (Phases 7+). See{" "}
          <Link to="/runs">Runs</Link> for full history.
        </span>
      </div>

      {createRun.isError && (
        <div className="error-panel" style={{ marginBottom: 16 }}>
          Run failed to start: {String(createRun.error)}
        </div>
      )}
      {createRun.isSuccess && (
        <div className="audit-card" style={{ marginBottom: 16 }}>
          <div className="audit-card__header">
            <span className="audit-card__name">{createRun.data.run_id}</span>
            <span>{createRun.data.stopped_reason === "error" ? "ERROR" : createRun.data.terminal_status}</span>
          </div>
          {createRun.data.diff && (
            <p className="section-note" style={{ margin: "8px 0 0" }}>
              {createRun.data.diff.nodes_status_changed.length} status change(s),{" "}
              {createRun.data.diff.nodes_added.length} node(s) added,{" "}
              {createRun.data.diff.new_falsifications.length} new falsification(s),{" "}
              {createRun.data.diff.new_calculations.length} new calculation(s).{" "}
              <Link to={`/runs`}>View in Runs →</Link>
            </p>
          )}
          {createRun.data.error && <p className="audit-card__issues">{createRun.data.error}</p>}
        </div>
      )}

      <ol className="execution-ladder">
        {STAGES.map((stage) => {
          const isAudit = stage.label === "AUDIT";
          const status = isAudit
            ? (state.data ? (state.data.all_audits_passed ? "PASS" : "FAIL") : "…")
            : "NOT IMPLEMENTED";
          return (
            <li key={stage.id} className={`execution-stage execution-stage--${isAudit ? (status === "PASS" ? "pass" : "fail") : "not-implemented"}`}>
              <span className="execution-stage__id">{stage.id}</span>
              <span className="execution-stage__label">{stage.label}</span>
              <span className="execution-stage__status">{status}</span>
            </li>
          );
        })}
      </ol>

      <h2>Self-Audit Detail (real, from compiler/verification/self_audit.py)</h2>
      {audits.data && (
        <table className="data-table">
          <thead><tr><th>Audit</th><th>Result</th><th>Issues</th></tr></thead>
          <tbody>
            {audits.data.map((a) => (
              <tr key={a.name}>
                <td>{a.name}</td>
                <td>{a.passed ? "PASS" : "FAIL"}</td>
                <td>{a.issues.length ? a.issues.join("; ") : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2>Research Ledger (live tail)</h2>
      <p className="section-note">
        Polled every few seconds from <code>GET /api/ledger</code> -- append-only, real events only
        (RUN_STARTED/RUN_COMPLETED today; LITERATURE_SEARCH/CANDIDATE_CREATED/PROOF_ATTEMPTED/etc.
        arrive with the research engine and proof/falsification workspaces, Phases 7-8).
      </p>
      {ledger.data && ledger.data.length === 0 && <p className="section-note">No ledger events yet.</p>}
      {ledger.data && ledger.data.length > 0 && (
        <table className="data-table">
          <thead><tr><th>Time</th><th>Run</th><th>Action</th><th>Status</th></tr></thead>
          <tbody>
            {[...ledger.data].reverse().map((e) => (
              <tr key={e.event_id}>
                <td>{e.timestamp}</td>
                <td>{e.run_id ? <code>{e.run_id}</code> : "—"}</td>
                <td>{e.action}</td>
                <td>{e.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <NotImplemented
        feature="Frontier selection → research → candidate generation → prove → falsify → promote/reject → new frontier"
        reason="POST /api/runs exists now (Phase 6) but only drives a full, untargeted compiler
          rebuild. The transparent frontier-ranked, targeted research cycle described in the brief
          requires the Research Orchestrator and Hypothesis Engine (Phase 7) and the proof/
          falsification workspaces (Phase 8), none of which exist yet."
      />
    </div>
  );
}
