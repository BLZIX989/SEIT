import "@testing-library/jest-dom/vitest";

// jsdom has no ResizeObserver; React Flow (used by the MDCL graph
// screen) requires one to observe its canvas container. This is a
// test-environment shim only -- it does not affect real browser
// rendering, which has a native ResizeObserver.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverStub;
