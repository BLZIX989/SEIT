import { useNavigate, useParams } from "react-router-dom";
import { NodeDetailPanel } from "../graph/NodeDetailPanel";

/**
 * Standalone, deep-linkable Node/DER inspector (Phase 5, brief section
 * VII "node selection reveals a large detail panel"). Reuses the same
 * NodeDetailPanel the interactive graph uses on click -- this route
 * exists so any other screen (chainlink arrows, provenance references,
 * a future search box) can link straight to a node without requiring
 * the graph to be open first.
 */
export function NodeInspector() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="node-inspector-screen">
      <h1>Node Inspector</h1>
      <p className="section-note">
        Full detail for a single MDCL node, read live from <code>GET /api/nodes/:id</code>.
      </p>
      <NodeDetailPanel
        nodeId={id ?? null}
        onSelectNode={(next) => navigate(`/nodes/${encodeURIComponent(next)}`)}
        onClose={() => navigate("/graph")}
      />
    </div>
  );
}
