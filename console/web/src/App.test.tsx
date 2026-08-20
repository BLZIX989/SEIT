import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

function renderAt(path: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

// Minimal, shape-valid stub responses per endpoint -- just enough for
// components to render past their loading state without crashing on a
// missing field. These are NOT used to assert canonical numbers
// anywhere (that's console/api/tests' job against the real
// repository); they exist only so routing/rendering tests don't need
// a live backend.
const STUB_RESPONSES: Record<string, unknown> = {
  "/api/health": { status: "ok", service: "uoc-research-console-api", phase: 3 },
  "/api/state": {
    total_nodes: 0, by_status: {}, by_kind: {}, terminal_status: null,
    all_audits_passed: true, audits: [], fc005_terminal_status: null,
    frontier_size: 0, generated_from: {},
  },
  "/api/mdcl": { types: [], objects: [], transformations: [], equations: [], status_matrix: [] },
  "/api/nodes": [],
  "/api/frontier": [],
  "/api/audits": [],
  "/api/chainlink": { arrows: [], note: "" },
  "/api/fc005": { terminal_status: null },
  "/api/runs": [],
  "/api/ledger": [],
};

const STUB_NODE_DETAIL = {
  id: "A-001", kind: "Object", status: "VERIFIED", role: "upstream_construction",
  raw: {}, dependencies: [], dependents: [], provenance: null, proofs: [],
  calculations: [], falsifications: [], superseding_nodes: [],
  superseding_nodes_note: "NOT_IMPLEMENTED",
};

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      if (/\/api\/nodes\/[^/]+$/.test(url)) {
        return new Response(JSON.stringify(STUB_NODE_DETAIL), { status: 200 });
      }
      const path = Object.keys(STUB_RESPONSES).find((p) => url.includes(p));
      const body = path ? STUB_RESPONSES[path] : {};
      return new Response(JSON.stringify(body), { status: 200 });
    }),
  );
});

describe("App routing", () => {
  it("renders the Overview screen at /", async () => {
    renderAt("/");
    // TanStack Query resolves async even against a stubbed fetch; the
    // heading renders once the initial query settles.
    expect(await screen.findByRole("heading", { name: "Current Theory State" })).toBeInTheDocument();
  });

  it("renders the Dependency Graph screen with live node/frontier data (Phase 4, no NOT IMPLEMENTED panel)", async () => {
    renderAt("/graph");
    expect(await screen.findByRole("heading", { name: "Dependency Graph" })).toBeInTheDocument();
    // Phase 4 replaced the placeholder table with a real React Flow
    // graph -- this screen must not show NOT IMPLEMENTED anymore.
    expect(screen.queryByText("NOT IMPLEMENTED")).not.toBeInTheDocument();
  });

  it("renders all 15 primary nav items", () => {
    renderAt("/");
    const expected = [
      "Overview", "Dependency Graph", "Theory State", "Derivation Lab", "Research",
      "Hypotheses", "Execution", "Proofs", "Falsification", "Literature", "Provenance",
      "Audits", "Runs", "Registries", "Settings",
    ];
    for (const label of expected) {
      expect(screen.getByRole("link", { name: label })).toBeInTheDocument();
    }
  });

  it("renders the standalone Node Inspector at /nodes/:id with live data (Phase 5)", async () => {
    renderAt("/nodes/A-001");
    expect(await screen.findByRole("heading", { name: "Node Inspector" })).toBeInTheDocument();
    expect(await screen.findByText("A-001")).toBeInTheDocument();
  });

  it("renders screens that have no backend yet with an explicit NOT IMPLEMENTED panel, never fake success", () => {
    for (const path of ["/derivation-lab", "/research", "/hypotheses", "/literature"]) {
      const { unmount } = renderAt(path);
      expect(screen.getByText("NOT IMPLEMENTED")).toBeInTheDocument();
      unmount();
    }
  });

  it("renders the Runs screen with real (empty) history, no NOT IMPLEMENTED panel (Phase 6)", async () => {
    renderAt("/runs");
    expect(await screen.findByRole("heading", { name: "Runs" })).toBeInTheDocument();
    expect(await screen.findByText("No runs yet. Trigger one from the Execution Console.")).toBeInTheDocument();
    expect(screen.queryByText("NOT IMPLEMENTED")).not.toBeInTheDocument();
  });

  it("renders the Execution screen with a real RUN THEORY SEARCH trigger (Phase 6)", async () => {
    renderAt("/execution");
    expect(await screen.findByRole("button", { name: "[ RUN THEORY SEARCH ]" })).toBeInTheDocument();
    expect(await screen.findByText("No ledger events yet.")).toBeInTheDocument();
  });
});
