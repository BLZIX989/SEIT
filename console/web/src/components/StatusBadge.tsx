/**
 * Renders a canonical Status value with a fixed, documented color
 * mapping. The mapping exists only here -- no other component may
 * invent its own color-to-status association (brief section VII: "Node
 * colors/status must come from canonical status").
 */
export const STATUS_COLORS: Record<string, string> = {
  VERIFIED: "#2e7d5b",
  DERIVED: "#3d7fb0",
  CALCULATED: "#5b6fb0",
  CONDITIONAL: "#9a7d2e",
  PROPOSED: "#7a7a7a",
  OPEN: "#5a5a5a",
  FAIL: "#b0522e",
  FALSIFIED: "#b02e2e",
};

export function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] ?? "#888888";
  return (
    <span
      className="status-badge"
      style={{ backgroundColor: color }}
      title={STATUS_COLORS[status] ? undefined : "unrecognized status value"}
    >
      {status}
    </span>
  );
}
