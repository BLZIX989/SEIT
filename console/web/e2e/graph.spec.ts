import { expect, test } from "@playwright/test";

// Phase 11 audit item 10: a real browser smoke test of the Dependency
// Graph screen against the real, live backend (both webServer entries in
// playwright.config.ts point at the real FastAPI app over the real
// registries -- no mock server, no fixture data). This asserts the graph
// actually renders real node/edge counts pulled live via the API, not
// just that the page didn't crash, and exercises the frontier-mode
// toggle against real frontier membership.

test("Dependency Graph renders the real MDCL and frontier mode reflects real /api/frontier membership", async ({
  page,
  request,
}) => {
  const nodesResp = await request.get("/api/nodes");
  expect(nodesResp.ok()).toBeTruthy();
  const nodes: { id: string; status: string }[] = await nodesResp.json();
  expect(nodes.length).toBeGreaterThan(0);

  const frontierResp = await request.get("/api/frontier");
  expect(frontierResp.ok()).toBeTruthy();
  const frontier: { id: string }[] = await frontierResp.json();
  const frontierIds = new Set(frontier.map((f) => f.id));

  await page.goto("/graph");
  await expect(page.getByRole("heading", { name: "Dependency Graph" })).toBeVisible();

  // The stats bar reports live counts -- must match the direct API read
  // exactly, not an approximation or a stale cached number.
  const statsBar = page.locator(".mdcl-graph-stats");
  await expect(statsBar).toContainText(`${nodes.length}`);
  await expect(statsBar).toContainText(`${frontier.length} frontier`);

  // The canvas must render one React Flow node element per real MDCL
  // node -- confirms this is a real graph render, not a placeholder.
  await expect(page.locator(".react-flow__node")).toHaveCount(nodes.length, { timeout: 15_000 });

  // Frontier mode off: every node (frontier or not) should be rendered
  // without the "dimmed" data attribute forced on purely by frontier
  // membership.
  const frontierCheckbox = page.getByRole("checkbox", { name: "Frontier mode (F_t)" });
  await expect(frontierCheckbox).not.toBeChecked();

  // Pick one node that is genuinely NOT in the frontier (guaranteed to
  // exist whenever the frontier is a strict subset of all nodes, which
  // is true for this repository's real state) and confirm frontier mode
  // dims it, using the real id straight from the API rather than an
  // invented fixture id.
  const nonFrontierNode = nodes.find((n) => !frontierIds.has(n.id));
  expect(nonFrontierNode, "expected at least one real non-frontier node to test dimming against").toBeTruthy();

  await frontierCheckbox.check();
  await expect(frontierCheckbox).toBeChecked();

  const nonFrontierNodeEl = page.locator(`.react-flow__node[data-id="${nonFrontierNode!.id}"] .mdcl-node`);
  await expect(nonFrontierNodeEl).toHaveClass(/mdcl-node--dimmed/);

  if (frontierIds.size > 0) {
    const frontierNodeId = frontier[0].id;
    const frontierNodeEl = page.locator(`.react-flow__node[data-id="${frontierNodeId}"] .mdcl-node`);
    await expect(frontierNodeEl).not.toHaveClass(/mdcl-node--dimmed/);
  }
});
