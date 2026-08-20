/**
 * Border-color mapping for the `role` field, the one genuinely
 * categorical grouping present in the registries
 * (upstream_construction / comparison / observational_output --
 * verified directly against object_registry.json /
 * transformation_registry.json / equation_registry.json). This is the
 * real substitute for the "named colored cluster" pattern in the
 * design references -- it labels a real field instead of inventing
 * thematic groupings the data doesn't have.
 */
export const ROLE_BORDER_COLORS: Record<string, string> = {
  upstream_construction: "#c9942f",
  comparison: "#3f8fc9",
  observational_output: "#8f5fc9",
};

export const ROLE_LABELS: Record<string, string> = {
  upstream_construction: "Upstream Construction",
  comparison: "Comparison",
  observational_output: "Observational Output",
};
