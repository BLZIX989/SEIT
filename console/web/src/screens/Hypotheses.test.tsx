import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Hypotheses } from "./Hypotheses";

const NODES = [{ id: "NODE-A", kind: "Object", status: "OPEN", role: "upstream_construction", dependencies: [] }];

let hypotheses: Record<string, unknown>[] = [];
let nextId = 1;

function stubFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input.toString();
      const method = init?.method ?? "GET";

      if (url.includes("/api/nodes")) return new Response(JSON.stringify(NODES), { status: 200 });

      if (method === "POST" && url.includes("/api/hypotheses") && !url.includes("transition")) {
        const body = JSON.parse(String(init?.body));
        const id = `HYP-${String(nextId++).padStart(4, "0")}`;
        const now = new Date().toISOString();
        const record = {
          id, statement: body.statement, target_node_id: body.target_node_id,
          dependencies: [], assumptions: body.assumptions ?? [], evidence: [], tests: [],
          status: "PROPOSED", created_at: now, updated_at: now, provenance: {}, superseded_by: null,
        };
        const isDuplicate = hypotheses.some((h) => h.statement === body.statement && h.target_node_id === body.target_node_id);
        hypotheses.push(record);
        return new Response(JSON.stringify({
          hypothesis: record,
          possible_duplicates: isDuplicate
            ? [{ id: hypotheses[0].id, statement: hypotheses[0].statement, status: hypotheses[0].status, match_confidence: "exact_normalized_match", similarity: 1.0 }]
            : [],
        }), { status: 201 });
      }

      if (url.includes("/api/hypotheses/") && url.includes("/transition")) {
        return new Response(JSON.stringify(hypotheses[0]), { status: 200 });
      }

      if (url.match(/\/api\/hypotheses\/[^/]+$/)) {
        const id = url.split("/").pop();
        const current = hypotheses.find((h) => h.id === id);
        return new Response(JSON.stringify({ current, history: [current] }), { status: 200 });
      }

      if (url.includes("/api/hypotheses")) return new Response(JSON.stringify(hypotheses), { status: 200 });

      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );
}

function renderScreen() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <Hypotheses />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Hypotheses screen", () => {
  beforeEach(() => {
    hypotheses = [];
    nextId = 1;
    stubFetch();
  });

  it("creates a hypothesis via the real form and lists it", async () => {
    renderScreen();
    // Wait for the real node list to load -- selecting NODE-A before its
    // <option> exists is a silent no-op in jsdom, not an error.
    await screen.findByRole("option", { name: "NODE-A (OPEN)" });

    fireEvent.change(screen.getByLabelText("Target node"), { target: { value: "NODE-A" } });
    fireEvent.change(screen.getByLabelText("Statement"), { target: { value: "a real statement about NODE-A" } });
    expect((screen.getByLabelText("Target node") as HTMLSelectElement).value).toBe("NODE-A");
    fireEvent.click(screen.getByRole("button", { name: "Propose hypothesis" }));

    // Appears twice once created: once in the "All hypotheses" table row,
    // once in the auto-opened detail panel's header.
    const matches = await screen.findAllByText("HYP-0001");
    expect(matches.length).toBeGreaterThanOrEqual(1);
  });

  it("surfaces a possible-duplicate warning for a repeated statement on the same node", async () => {
    renderScreen();
    await screen.findByRole("option", { name: "NODE-A (OPEN)" });

    const propose = async (statement: string) => {
      fireEvent.change(screen.getByLabelText("Target node"), { target: { value: "NODE-A" } });
      fireEvent.change(screen.getByLabelText("Statement"), { target: { value: statement } });
      fireEvent.click(screen.getByRole("button", { name: "Propose hypothesis" }));
      await waitFor(() => expect(screen.getByLabelText("Statement")).toHaveValue(""));
    };

    await propose("the exact same statement");
    await propose("the exact same statement");

    expect(await screen.findByText(/Possible duplicate/)).toBeInTheDocument();
  });
});
