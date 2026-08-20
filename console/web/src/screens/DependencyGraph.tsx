import { MdclGraph } from "../graph/MdclGraph";

/**
 * Interactive MDCL dependency graph (Phase 4, brief section VII).
 * All node/edge/status/role/frontier data comes from GET /api/nodes and
 * GET /api/frontier -- the same live registries every other screen
 * reads. Layout is dagre over the real dependency edges (no
 * force-directed approximation, no invented thematic clustering).
 */
export function DependencyGraph() {
  return (
    <div className="dependency-graph-screen">
      <h1>Dependency Graph</h1>
      <p className="section-note">
        Every node, edge, status color, and dependency arrow below is read live from the canonical
        registries. Click a node to inspect it; dependency/dependent highlighting and frontier mode
        (F_t) use the same admissibility rule the compiler itself uses to decide what can execute next.
      </p>
      <MdclGraph />
    </div>
  );
}
