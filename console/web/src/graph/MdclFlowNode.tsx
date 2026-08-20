import { Handle, Position, type NodeProps } from "@xyflow/react";
import { STATUS_COLORS } from "../components/StatusBadge";
import { ROLE_BORDER_COLORS } from "./roleColors";
import type { GraphNodeData } from "./layout";

const KIND_TAG: Record<string, string> = {
  Object: "O",
  Transformation: "T",
  Equation: "E",
};

export function MdclFlowNode({ data, selected }: NodeProps & { data: GraphNodeData }) {
  const fill = STATUS_COLORS[data.status] ?? "#888888";
  const border = ROLE_BORDER_COLORS[data.role] ?? "#555555";
  const isHighlighted = data.highlighted !== "none";

  return (
    <div
      className={`mdcl-node mdcl-node--${data.highlighted}${data.dimmed ? " mdcl-node--dimmed" : ""}${selected ? " mdcl-node--selected" : ""}`}
      style={{
        backgroundColor: fill,
        borderColor: isHighlighted || selected ? "#fff" : border,
      }}
      title={`${data.id} — ${data.kind} — ${data.status} — role: ${data.role}`}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <span className="mdcl-node__kind">{KIND_TAG[data.kind] ?? "?"}</span>
      <span className="mdcl-node__id">{data.id}</span>
      <span className="mdcl-node__status">{data.status}</span>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
}
