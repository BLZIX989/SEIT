import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ChainlinkView } from "./ChainlinkView";

const ARROW = {
  from_id: "DISTINCTION", to_id: "TRANSFORMATION-NODE",
  from_symbol: "Δ", to_symbol: "Γ",
  status: "OPEN", der_id: null, der_id_note: "NOT_IMPLEMENTED: no DER-id concept.",
  proof: [], dependencies: ["DISTINCTION"], assumptions: ["assumption text"],
  calculations: [], failures: [], open_obligations: ["DISTINCTION"],
  literature: [], literature_note: "NOT_IMPLEMENTED: no linkage field.",
  execution_status: "NOT_IMPLEMENTED",
};

function stubFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify({ arrows: [ARROW], note: "test note" }), { status: 200 })),
  );
}

function renderView() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ChainlinkView />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("ChainlinkView", () => {
  beforeEach(() => stubFetch());

  it("renders arrow chips from real chainlink data and no detail panel until clicked", async () => {
    renderView();
    expect(await screen.findByText("Δ")).toBeInTheDocument();
    expect(screen.queryByText("Open obligations (1)")).not.toBeInTheDocument();
  });

  it("opens the arrow detail panel on click, showing dependencies/obligations/notes honestly", async () => {
    renderView();
    const chip = await screen.findByText("Δ");
    fireEvent.click(chip.closest("button") as HTMLButtonElement);

    expect(await screen.findByText("Open obligations (1)")).toBeInTheDocument();
    expect(screen.getByText("NOT_IMPLEMENTED: no DER-id concept.")).toBeInTheDocument();
    expect(screen.getByText("NOT_IMPLEMENTED: no linkage field.")).toBeInTheDocument();
  });
});
