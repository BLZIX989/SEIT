import { StatusBadge } from "../components/StatusBadge";
import { useNode } from "../api/queries";

/**
 * Large detail panel shown on node selection (brief section VII).
 * Every field is a real value from GET /api/nodes/:id -- dependencies,
 * dependents, provenance, proofs, calculations, falsification matches
 * (with honest match-confidence tiers) -- nothing here is inferred or
 * fabricated for display purposes.
 */
export function NodeDetailPanel({
  nodeId,
  onSelectNode,
  onClose,
}: {
  nodeId: string | null;
  onSelectNode: (id: string) => void;
  onClose: () => void;
}) {
  const node = useNode(nodeId ?? undefined);

  if (!nodeId) {
    return (
      <div className="node-detail-panel node-detail-panel--empty">
        <p className="section-note">Select a node to inspect its dependencies, provenance, proofs, and falsification matches.</p>
      </div>
    );
  }

  return (
    <div className="node-detail-panel">
      <div className="node-detail-panel__header">
        <h3><code>{nodeId}</code></h3>
        <button className="btn-close" onClick={onClose} aria-label="Close detail panel">×</button>
      </div>

      {node.isLoading && <p>Loading node…</p>}
      {node.isError && <div className="error-panel">Failed to load node: {String(node.error)}</div>}

      {node.data && (
        <>
          <div className="node-detail-panel__meta">
            <StatusBadge status={node.data.status} />
            <span className="tag">{node.data.kind}</span>
            <span className="tag">role: {node.data.role}</span>
          </div>

          <h4>Dependencies ({node.data.dependencies.length})</h4>
          {node.data.dependencies.length === 0 && <p className="section-note">None — root node.</p>}
          <ul className="node-ref-list">
            {node.data.dependencies.map((d) => (
              <li key={d}><button className="link-button" onClick={() => onSelectNode(d)}>{d}</button></li>
            ))}
          </ul>

          <h4>Dependents ({node.data.dependents.length})</h4>
          {node.data.dependents.length === 0 && <p className="section-note">None — nothing downstream depends on this node yet.</p>}
          <ul className="node-ref-list">
            {node.data.dependents.map((d) => (
              <li key={d}><button className="link-button" onClick={() => onSelectNode(d)}>{d}</button></li>
            ))}
          </ul>

          <h4>Provenance</h4>
          {node.data.provenance ? (
            <table className="data-table">
              <tbody>
                <tr><td>Source</td><td>{node.data.provenance.source || "—"}</td></tr>
                <tr><td>Status (provenance record)</td><td>{node.data.provenance.status}</td></tr>
                <tr><td>Execution timestamp</td><td>{node.data.provenance.execution_timestamp || "—"}</td></tr>
                <tr><td>Git commit</td><td><code>{node.data.provenance.git_commit || "—"}</code></td></tr>
                <tr><td>Calculation ID</td><td>{node.data.provenance.calculation_id || "—"}</td></tr>
              </tbody>
            </table>
          ) : <p className="section-note">No provenance record.</p>}

          <h4>Proofs ({node.data.proofs.length})</h4>
          {node.data.proofs.length === 0 && <p className="section-note">No proof record referencing this node as a transformation_id.</p>}
          {node.data.proofs.length > 0 && (
            <pre className="audit-card__details">{JSON.stringify(node.data.proofs, null, 2)}</pre>
          )}

          <h4>Calculations ({node.data.calculations.length})</h4>
          {node.data.calculations.length === 0 && <p className="section-note">No calculation linked via provenance.calculation_id.</p>}
          {node.data.calculations.length > 0 && (
            <pre className="audit-card__details">{JSON.stringify(node.data.calculations, null, 2)}</pre>
          )}

          <h4>Falsification matches ({node.data.falsifications.length})</h4>
          {node.data.falsifications.length === 0 && <p className="section-note">No falsification record text-matches this node.</p>}
          {node.data.falsifications.map((f, i) => (
            <div key={i} className="audit-card">
              <div className="audit-card__header">
                <span className="tag">{f.match_confidence}</span>
              </div>
              <pre className="audit-card__details">{JSON.stringify(f.record, null, 2)}</pre>
            </div>
          ))}

          <h4>Supersession</h4>
          <p className="section-note">{node.data.superseding_nodes_note}</p>

          <h4>Raw registry entry</h4>
          <pre className="audit-card__details">{JSON.stringify(node.data.raw, null, 2)}</pre>
        </>
      )}
    </div>
  );
}
