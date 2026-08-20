/**
 * Dagre layout over the real dependency graph. Positions are computed
 * from actual `dependencies` edges returned by /api/nodes -- there is
 * no force-directed "make it look nice" simulation and no invented
 * spatial clustering. Node position encodes real dependency structure
 * (rank = topological depth), matching the brief's rule that the graph
 * must render the canonical dependency graph, not a stylized
 * approximation of it.
 */
import dagre from "@dagrejs/dagre";
import type { Edge, Node } from "@xyflow/react";
import type { NodeKind, NodeSummary } from "../api/types";

export const NODE_WIDTH = 168;
export const NODE_HEIGHT = 56;

export interface GraphNodeData extends Record<string, unknown> {
  id: string;
  kind: NodeKind;
  status: string;
  role: string;
  dimmed: boolean;
  highlighted: "none" | "selected" | "dependency" | "dependent" | "frontier" | "match";
}

export function buildGraphElements(nodes: NodeSummary[]): {
  flowNodes: Node<GraphNodeData>[];
  flowEdges: Edge[];
} {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", nodesep: 28, ranksep: 90 });
  g.setDefaultEdgeLabel(() => ({}));

  const knownIds = new Set(nodes.map((n) => n.id));

  for (const n of nodes) {
    g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  }
  for (const n of nodes) {
    for (const dep of n.dependencies) {
      // Only draw edges to dependencies that actually resolve to a
      // known node -- an unresolved reference is a data-quality fact
      // to surface elsewhere (node detail panel), not something to
      // silently draw as if it were a real edge.
      if (knownIds.has(dep)) g.setEdge(dep, n.id);
    }
  }

  dagre.layout(g);

  const flowNodes: Node<GraphNodeData>[] = nodes.map((n) => {
    const pos = g.node(n.id);
    return {
      id: n.id,
      type: "mdclNode",
      position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 },
      data: {
        id: n.id,
        kind: n.kind,
        status: n.status,
        role: n.role,
        dimmed: false,
        highlighted: "none",
      },
    };
  });

  const flowEdges: Edge[] = [];
  for (const n of nodes) {
    for (const dep of n.dependencies) {
      if (knownIds.has(dep)) {
        flowEdges.push({
          id: `${dep}->${n.id}`,
          source: dep,
          target: n.id,
          data: { dimmed: false, highlighted: false },
        });
      }
    }
  }

  return { flowNodes, flowEdges };
}
