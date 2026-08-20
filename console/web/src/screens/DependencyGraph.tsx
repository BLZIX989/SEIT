import { NotImplemented } from "../components/NotImplemented";
import { StatusBadge } from "../components/StatusBadge";
import { useFrontier, useNodes } from "../api/queries";

/**
 * Phase 3 stub: real node/frontier data rendered as a table, since
 * that already exists via /api/nodes and /api/frontier. The
 * interactive pan/zoom/cluster graph itself (brief section VII) is
 * Phase 4 work and is not faked here with a static image or a
 * non-interactive placeholder graphic.
 */
export function DependencyGraph() {
  const nodes = useNodes();
  const frontier = useFrontier();
  const frontierIds = new Set((frontier.data ?? []).map((f) => f.id));

  return (
    <div>
      <h1>Dependency Graph</h1>
      <NotImplemented
        feature="Interactive MDCL graph (pan/zoom/search/filter/clusters)"
        reason="Phase 4 of the implementation plan. The data this view will render already exists
          and is shown below as a plain table in the meantime -- real node/status/dependency data,
          not a mock graph."
      />
      {nodes.isLoading && <p>Loading nodes…</p>}
      {nodes.data && (
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Kind</th>
              <th>Status</th>
              <th>Dependencies</th>
              <th>Frontier?</th>
            </tr>
          </thead>
          <tbody>
            {nodes.data.map((n) => (
              <tr key={n.id} className={frontierIds.has(n.id) ? "row--frontier" : undefined}>
                <td><code>{n.id}</code></td>
                <td>{n.kind}</td>
                <td><StatusBadge status={n.status} /></td>
                <td>{n.dependencies.length ? n.dependencies.join(", ") : "—"}</td>
                <td>{frontierIds.has(n.id) ? "yes" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
