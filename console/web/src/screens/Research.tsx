import { Link } from "react-router-dom";
import { NotImplemented } from "../components/NotImplemented";
import { StatusBadge } from "../components/StatusBadge";
import { useFrontier, useHypotheses } from "../api/queries";

/**
 * The Research Orchestrator is still mostly NOT_IMPLEMENTED -- there is
 * no literature search, candidate generation, or evidence
 * classification backend in this repository (Phase 0's finding still
 * holds). What Phase 7 makes real is the frontier ranking's one new
 * transparent input, `historical_failure_rate`, computed from actual
 * Hypothesis records rather than invented -- and a direct link from
 * each frontier node into what has already been tried against it.
 */
export function Research() {
  const frontier = useFrontier();
  const hypotheses = useHypotheses();

  const hypothesesByNode = new Map<string, number>();
  for (const h of hypotheses.data ?? []) {
    hypothesesByNode.set(h.target_node_id, (hypothesesByNode.get(h.target_node_id) ?? 0) + 1);
  }

  return (
    <div>
      <h1>Research</h1>
      <p className="section-note">
        Frontier ranking inputs -- transparent, real, never a synthesized "scientific significance"
        score (brief section XV). Click a node's hypothesis count to see what has already been
        tried against it, and why it did or didn't work, before proposing another one.
      </p>

      {frontier.data && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Node</th><th>Status</th><th>Downstream unlock count</th>
              <th>Historical failure rate</th><th>Hypotheses tried</th>
            </tr>
          </thead>
          <tbody>
            {frontier.data.map((f) => (
              <tr key={f.id}>
                <td><Link to={`/nodes/${encodeURIComponent(f.id)}`}>{f.id}</Link></td>
                <td><StatusBadge status={f.status} /></td>
                <td>{f.downstream_unlock_count}</td>
                <td>{f.historical_failure_rate === null ? "no data yet" : `${Math.round(f.historical_failure_rate * 100)}%`}</td>
                <td>
                  <Link to={`/hypotheses`}>{hypothesesByNode.get(f.id) ?? 0}</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <NotImplemented
        feature="Literature search, candidate generation, evidence classification
          (ESTABLISHED PHYSICS / DERIVED WITHIN UOC / EXTERNALLY SUPPORTED / PROPOSED / UNVERIFIED /
          FALSIFIED / CONJECTURAL)"
        reason="No literature ingestion or candidate-generation backend exists in this repository
          (confirmed in Phase 0 reconnaissance) -- the Hypothesis Engine (Phase 7, see Hypotheses
          screen) lets a researcher record and track hypotheses by hand, but nothing here searches
          literature or generates candidates automatically yet."
      />
    </div>
  );
}
