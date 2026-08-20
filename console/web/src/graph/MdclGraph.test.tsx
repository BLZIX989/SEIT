import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MdclGraph } from "./MdclGraph";

// A small, realistic 4-node dependency chain (A -> B -> C, D independent)
// exercising the real /api/nodes and /api/frontier shapes -- not a
// crash-only smoke test.
const NODES = [
  { id: "A-001", kind: "Object", status: "VERIFIED", role: "upstream_construction", dependencies: [] },
  { id: "B-002", kind: "Object", status: "DERIVED", role: "comparison", dependencies: ["A-001"] },
  { id: "C-003", kind: "Equation", status: "OPEN", role: "observational_output", dependencies: ["B-002"] },
  { id: "D-004", kind: "Transformation", status: "PROPOSED", role: "upstream_construction", dependencies: [] },
];

const FRONTIER = [
  { id: "D-004", kind: "Transformation", status: "PROPOSED", unresolved_dependency_count: 0, resolved_dependencies: [], downstream_unlock_count: 0 },
];

function stubFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/api/nodes/")) {
        const id = url.split("/").pop();
        const node = NODES.find((n) => n.id === id);
        const dependents = NODES.filter((n) => n.dependencies.includes(id ?? "")).map((n) => n.id);
        return new Response(
          JSON.stringify({
            ...node,
            raw: node,
            dependents,
            provenance: null,
            proofs: [],
            calculations: [],
            falsifications: [],
            superseding_nodes: [],
            superseding_nodes_note: "NOT_IMPLEMENTED",
          }),
          { status: 200 },
        );
      }
      if (url.includes("/api/nodes")) return new Response(JSON.stringify(NODES), { status: 200 });
      if (url.includes("/api/frontier")) return new Response(JSON.stringify(FRONTIER), { status: 200 });
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );
}

function renderGraph() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MdclGraph />
    </QueryClientProvider>,
  );
}

describe("MdclGraph", () => {
  beforeEach(() => {
    stubFetch();
  });

  it("renders real node/edge/frontier counts from the API, not placeholders", async () => {
    renderGraph();
    expect(await screen.findByText("4")).toBeInTheDocument(); // node count
    expect(screen.getByText("2")).toBeInTheDocument(); // edge count (A->B, B->C; D independent)
    expect(screen.getByText("1")).toBeInTheDocument(); // frontier count
  });

  it("renders every node id from the API response", async () => {
    renderGraph();
    await screen.findByText("A-001");
    for (const n of NODES) {
      expect(screen.getByText(n.id)).toBeInTheDocument();
    }
  });

  it("shows role legend counts computed from real registry data", async () => {
    renderGraph();
    const note = await screen.findByText(/Role legend/);
    expect(note.textContent).toContain("2 upstream_construction");
    expect(note.textContent).toContain("1 comparison");
    expect(note.textContent).toContain("1 observational_output");
  });
});
