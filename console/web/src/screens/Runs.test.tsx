import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Runs } from "./Runs";

const RUN_1 = {
  run_id: "RUN-0001", started_at: "t1", completed_at: "t1", trigger: "full_rebuild", scope: "full_rebuild",
  target_node_ids: [], pre_state_hash: "a", post_state_hash: "b",
  diff: { nodes_added: [], nodes_status_changed: [], nodes_unchanged: 0, new_falsifications: [], new_calculations: [], audit_deltas: [] },
  test_suite_result: null, self_audit_result: null, terminal_status: "CONDITIONALLY_CLOSED", stopped_reason: "completed", error: null,
};
const RUN_2 = {
  ...RUN_1, run_id: "RUN-0002", pre_state_hash: "b", post_state_hash: "c",
  diff: { nodes_added: ["NEW-X"], nodes_status_changed: [{ id: "A", old_status: "OPEN", new_status: "VERIFIED" }], nodes_unchanged: 3, new_falsifications: [], new_calculations: [], audit_deltas: [] },
};

const COMPARISON = {
  from_run_id: "RUN-0001", to_run_id: "RUN-0002", runs_in_range: ["RUN-0002"],
  nodes_added: ["NEW-X"], nodes_status_changed: [{ id: "A", old_status: "OPEN", new_status: "VERIFIED" }],
  new_falsifications: [], new_calculations: [], audit_deltas: [],
  from_terminal_status: "CONDITIONALLY_CLOSED", to_terminal_status: "CONDITIONALLY_CLOSED",
};

function stubFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/api/runs/compare")) return new Response(JSON.stringify(COMPARISON), { status: 200 });
      if (url.includes("/api/runs")) return new Response(JSON.stringify([RUN_1, RUN_2]), { status: 200 });
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );
}

function renderScreen() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <Runs />
    </QueryClientProvider>,
  );
}

describe("Runs screen comparison (Phase 10)", () => {
  beforeEach(() => stubFetch());

  it("shows the compare picker once there are 2+ runs and renders a real comparison on selection", async () => {
    renderScreen();
    await screen.findByRole("heading", { name: "Compare runs" });

    const [fromSelect, toSelect] = screen.getAllByRole("combobox");
    fireEvent.change(fromSelect, { target: { value: "RUN-0001" } });
    fireEvent.change(toSelect, { target: { value: "RUN-0002" } });

    expect(await screen.findByText("NEW-X")).toBeInTheDocument();
    expect(await screen.findByText("Net status changes (1)")).toBeInTheDocument();
  });

  it("prompts to pick two different runs when from == to", async () => {
    renderScreen();
    await screen.findByRole("heading", { name: "Compare runs" });
    const [fromSelect, toSelect] = screen.getAllByRole("combobox");
    fireEvent.change(fromSelect, { target: { value: "RUN-0001" } });
    fireEvent.change(toSelect, { target: { value: "RUN-0001" } });

    expect(await screen.findByText("Pick two different runs to compare.")).toBeInTheDocument();
  });
});
