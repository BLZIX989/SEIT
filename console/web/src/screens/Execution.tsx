import { NotImplemented } from "../components/NotImplemented";
import { useAudits, useStateRollup } from "../api/queries";

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
 * Brief section XIII's build-ladder view. Only stage 09 (AUDIT) has a
 * real backend today (/api/audits, wired to compiler/verification/
 * self_audit.py). Every other stage is rendered as NOT IMPLEMENTED
 * rather than a fake progress indicator -- there is no
 * POST /api/runs yet to actually drive stages 01-08/10-11.
 */
export function Execution() {
  const audits = useAudits();
  const state = useStateRollup();

  return (
    <div>
      <h1>Execution Console</h1>
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

      <NotImplemented
        feature="RUN THEORY SEARCH (frontier selection → research → candidate → compile →
          execute → prove → falsify → audit → promote/reject → new frontier)"
        reason="Backend required: POST /api/runs does not exist yet (Phase 6). Today, 'running the
          compiler' means invoking `python3 -m compiler.run_compiler` directly outside this
          console; the console can only display the result afterward."
      />
    </div>
  );
}
