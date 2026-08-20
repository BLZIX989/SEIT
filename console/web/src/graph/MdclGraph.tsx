import { Background, Controls, MiniMap, ReactFlow, type Node } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useMemo, useState } from "react";
import { STATUS_COLORS } from "../components/StatusBadge";
import type { NodeSummary } from "../api/types";
import { useFrontier, useNodes } from "../api/queries";
import { buildReverseDeps, collectAncestors, collectDescendants } from "./graphSelection";
import { buildGraphElements, type GraphNodeData } from "./layout";
import { MdclFlowNode } from "./MdclFlowNode";
import { NodeDetailPanel } from "./NodeDetailPanel";
import { ROLE_BORDER_COLORS, ROLE_LABELS } from "./roleColors";

const NODE_TYPES = { mdclNode: MdclFlowNode };

const ALL_STATUSES = Object.keys(STATUS_COLORS);

export function MdclGraph() {
  const nodesQuery = useNodes();
  const frontierQuery = useFrontier();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<Set<string>>(new Set(ALL_STATUSES));
  const [roleFilter, setRoleFilter] = useState<Set<string>>(new Set(Object.keys(ROLE_LABELS)));
  const [kindFilter, setKindFilter] = useState<Set<string>>(new Set(["Object", "Transformation", "Equation"]));
  const [frontierMode, setFrontierMode] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const allNodes = nodesQuery.data ?? [];
  const nodesById = useMemo(() => new Map(allNodes.map((n) => [n.id, n])), [allNodes]);
  const reverseDeps = useMemo(() => buildReverseDeps(allNodes), [allNodes]);
  const frontierIds = useMemo(() => new Set((frontierQuery.data ?? []).map((f) => f.id)), [frontierQuery.data]);

  const { flowNodes: baseNodes, flowEdges } = useMemo(() => buildGraphElements(allNodes), [allNodes]);

  const ancestorSet = selectedId ? collectAncestors(selectedId, nodesById) : null;
  const descendantSet = selectedId ? collectDescendants(selectedId, reverseDeps) : null;
  const searchLower = search.trim().toLowerCase();

  const passesFilter = (n: NodeSummary) =>
    statusFilter.has(n.status) && roleFilter.has(n.role) && kindFilter.has(n.kind) && (!frontierMode || frontierIds.has(n.id));

  const flowNodes: Node<GraphNodeData>[] = baseNodes.map((fn) => {
    const n = nodesById.get(fn.id);
    if (!n) return fn;
    const filterOk = passesFilter(n);
    const matchesSearch = searchLower.length > 0 && n.id.toLowerCase().includes(searchLower);

    let highlighted: GraphNodeData["highlighted"] = "none";
    if (selectedId === n.id) highlighted = "selected";
    else if (ancestorSet?.has(n.id)) highlighted = "dependency";
    else if (descendantSet?.has(n.id)) highlighted = "dependent";
    else if (searchLower && matchesSearch) highlighted = "match";
    else if (frontierMode && frontierIds.has(n.id)) highlighted = "frontier";

    const dimmed =
      !filterOk ||
      (searchLower.length > 0 && !matchesSearch && highlighted === "none") ||
      (selectedId !== null && highlighted === "none");

    return { ...fn, data: { ...fn.data, highlighted, dimmed } };
  });

  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const n of allNodes) counts[n.status] = (counts[n.status] ?? 0) + 1;
    return counts;
  }, [allNodes]);

  const roleCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const n of allNodes) counts[n.role] = (counts[n.role] ?? 0) + 1;
    return counts;
  }, [allNodes]);

  if (nodesQuery.isLoading) return <p>Loading MDCL graph…</p>;
  if (nodesQuery.isError) return <div className="error-panel">Failed to load nodes: {String(nodesQuery.error)}</div>;

  return (
    <div className="mdcl-graph-workspace">
      <div className="mdcl-graph-toolbar">
        <input
          className="graph-search"
          type="text"
          placeholder="Search node ID…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <label className="graph-toggle">
          <input type="checkbox" checked={frontierMode} onChange={(e) => setFrontierMode(e.target.checked)} />
          Frontier mode (F_t)
        </label>
        <FilterGroup label="Kind" options={["Object", "Transformation", "Equation"]} selected={kindFilter} onChange={setKindFilter} />
        <FilterGroup label="Status" options={ALL_STATUSES} selected={statusFilter} onChange={setStatusFilter} colors={STATUS_COLORS} />
        <FilterGroup label="Role" options={Object.keys(ROLE_LABELS)} selected={roleFilter} onChange={setRoleFilter} colors={ROLE_BORDER_COLORS} labels={ROLE_LABELS} />
      </div>

      <div className="mdcl-graph-stats">
        <span><strong>{allNodes.length}</strong> nodes</span>
        <span><strong>{flowEdges.length}</strong> edges</span>
        <span><strong>{frontierIds.size}</strong> frontier</span>
        {ALL_STATUSES.map((s) => (
          <span key={s} className="mdcl-graph-stats__status">
            <i style={{ backgroundColor: STATUS_COLORS[s] }} /> {s}: {statusCounts[s] ?? 0}
          </span>
        ))}
      </div>

      <div className="mdcl-graph-canvas-row">
        <div className="mdcl-graph-canvas">
          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            nodeTypes={NODE_TYPES}
            onNodeClick={(_, node) => setSelectedId(node.id === selectedId ? null : node.id)}
            fitView
            minZoom={0.05}
            maxZoom={2}
            proOptions={{ hideAttribution: true }}
          >
            <Background gap={24} />
            <Controls />
            <MiniMap
              pannable
              zoomable
              nodeColor={(n) => STATUS_COLORS[(n.data as GraphNodeData).status] ?? "#888"}
            />
          </ReactFlow>
        </div>
        <NodeDetailPanel nodeId={selectedId} onSelectNode={setSelectedId} onClose={() => setSelectedId(null)} />
      </div>

      <p className="section-note">
        Role legend (real registry field, {roleCounts.upstream_construction ?? 0} upstream_construction /{" "}
        {roleCounts.comparison ?? 0} comparison / {roleCounts.observational_output ?? 0} observational_output):
        node border color. Node fill: canonical status. Layout: dagre over real dependency edges (not force-directed,
        not clustered by invented theme).
      </p>
    </div>
  );
}

function FilterGroup({
  label,
  options,
  selected,
  onChange,
  colors,
  labels,
}: {
  label: string;
  options: string[];
  selected: Set<string>;
  onChange: (s: Set<string>) => void;
  colors?: Record<string, string>;
  labels?: Record<string, string>;
}) {
  const toggle = (opt: string) => {
    const next = new Set(selected);
    if (next.has(opt)) next.delete(opt);
    else next.add(opt);
    onChange(next);
  };
  return (
    <div className="filter-group">
      <span className="filter-group__label">{label}</span>
      {options.map((opt) => (
        <label key={opt} className={`filter-chip${selected.has(opt) ? " filter-chip--active" : ""}`}>
          <input type="checkbox" checked={selected.has(opt)} onChange={() => toggle(opt)} style={{ display: "none" }} />
          {colors?.[opt] && <i style={{ backgroundColor: colors[opt] }} />}
          {labels?.[opt] ?? opt}
        </label>
      ))}
    </div>
  );
}
