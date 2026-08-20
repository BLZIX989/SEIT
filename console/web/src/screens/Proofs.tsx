import { useState } from "react";
import { Link } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { useProofs } from "../api/queries";
import type { ProofRecordDetail } from "../api/types";

/**
 * Proof Workspace (Phase 8). Every row is a real proof_registry.json
 * entry, enriched with the transformation's real preconditions /
 * postconditions / assumptions and a live, independent circular-
 * dependency re-check ("Conclusion(T) in Premises(T)") -- computed on
 * every request from console/api/canonical/proof_check.py, never
 * assumed clean just because the compiler's own construction-time
 * guard should already prevent it.
 */
export function Proofs() {
  const proofs = useProofs();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const list = proofs.data ?? [];
  const selected = list.find((p) => p.id === selectedId) ?? null;
  const anyCircular = list.some((p) => p.circular_dependency.is_circular);

  return (
    <div>
      <h1>Proofs</h1>
      <p className="section-note">
        Every proof below is a real <code>proof_registry.json</code> entry. The circular-dependency
        column is re-computed live on every load, independent of the compiler's own build-time
        cycle guard -- this workspace never simply trusts that guard ran.
      </p>

      {anyCircular && (
        <div className="error-panel" style={{ marginBottom: 16 }}>
          CIRCULAR_DEPENDENCY detected in at least one proof below -- certification must not
          proceed for the affected node(s) until resolved.
        </div>
      )}

      {list.length === 0 && !proofs.isLoading && <p className="section-note">No proof records yet.</p>}

      {list.length > 0 && (
        <table className="data-table">
          <thead>
            <tr><th>ID</th><th>Node</th><th>Status</th><th>Open obligations</th><th>Circular?</th></tr>
          </thead>
          <tbody>
            {list.map((p) => (
              <tr key={p.id} className={p.id === selectedId ? "row--frontier" : undefined} style={{ cursor: "pointer" }} onClick={() => setSelectedId(p.id === selectedId ? null : p.id)}>
                <td><code>{p.id}</code></td>
                <td><Link to={`/nodes/${encodeURIComponent(p.transformation_id)}`} onClick={(e) => e.stopPropagation()}>{p.transformation_id}</Link></td>
                <td><StatusBadge status={p.status} /></td>
                <td>{p.open_obligations.length}</td>
                <td>{p.circular_dependency.is_circular
                  ? <span className="tag" style={{ color: "var(--status-bad)", borderColor: "var(--status-bad)" }}>CIRCULAR_DEPENDENCY</span>
                  : <span className="tag tag--executed">clean</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selected && <ProofDetail proof={selected} />}
    </div>
  );
}

function ProofDetail({ proof }: { proof: ProofRecordDetail }) {
  return (
    <div className="node-detail-panel" style={{ width: "auto", maxWidth: 760 }}>
      <div className="node-detail-panel__header">
        <h3><code>{proof.id}</code></h3>
      </div>

      {proof.circular_dependency.is_circular && (
        <div className="error-panel" style={{ marginBottom: 10 }}>
          CIRCULAR_DEPENDENCY: {proof.circular_dependency.cycle_path?.join(" → ")}
        </div>
      )}

      <p>{proof.statement}</p>
      <h4>Method</h4>
      <p className="section-note">{proof.method || "None recorded."}</p>

      <h4>Preconditions ({proof.preconditions.length})</h4>
      {proof.preconditions.length === 0 && <p className="section-note">None recorded.</p>}
      {proof.preconditions.length > 0 && <ul>{proof.preconditions.map((p, i) => <li key={i}>{p}</li>)}</ul>}

      <h4>Postconditions ({proof.postconditions.length})</h4>
      {proof.postconditions.length === 0 && <p className="section-note">None recorded.</p>}
      {proof.postconditions.length > 0 && <ul>{proof.postconditions.map((p, i) => <li key={i}>{p}</li>)}</ul>}

      <h4>Assumptions ({proof.assumptions.length})</h4>
      {proof.assumptions.length === 0 && <p className="section-note">None recorded.</p>}
      {proof.assumptions.length > 0 && <ul>{proof.assumptions.map((a, i) => <li key={i}>{a}</li>)}</ul>}

      <h4>Open obligations ({proof.open_obligations.length})</h4>
      {proof.open_obligations.length === 0
        ? <p className="section-note">None -- every declared dependency is already admissible/closed.</p>
        : (
          <ul className="node-ref-list">
            {proof.open_obligations.map((d) => (
              <li key={d}><Link className="link-button" to={`/nodes/${encodeURIComponent(d)}`}>{d}</Link></li>
            ))}
          </ul>
        )}
    </div>
  );
}
