/**
 * UI-side mirror of console/api/research/hypothesis_status.py's
 * ALLOWED_TRANSITIONS, used only to decide which transition buttons to
 * show. The server is the sole authority -- every transition is
 * re-validated there (POST /api/hypotheses/:id/transition returns 409
 * for anything not in that same map) -- this exists purely so the UI
 * doesn't offer a button that would be rejected on click.
 */
import type { HypothesisStatus } from "../api/types";

export const ALLOWED_TRANSITIONS: Record<HypothesisStatus, HypothesisStatus[]> = {
  PROPOSED: ["TESTING", "REJECTED", "BLOCKED"],
  TESTING: ["SUPPORTED", "REJECTED", "FALSIFIED", "BLOCKED"],
  SUPPORTED: ["DERIVED", "REJECTED", "FALSIFIED", "SUPERSEDED", "BLOCKED"],
  DERIVED: ["VERIFIED", "REJECTED", "FALSIFIED", "SUPERSEDED", "BLOCKED"],
  VERIFIED: ["SUPERSEDED"],
  BLOCKED: ["PROPOSED", "TESTING", "REJECTED"],
  REJECTED: [],
  FALSIFIED: [],
  SUPERSEDED: [],
};

export const HYPOTHESIS_STATUS_COLORS: Record<HypothesisStatus, string> = {
  PROPOSED: "#7a7a7a",
  TESTING: "#4d8fd6",
  SUPPORTED: "#3d7fb0",
  DERIVED: "#5b6fb0",
  VERIFIED: "#2e7d5b",
  REJECTED: "#8a5a3a",
  FALSIFIED: "#b02e2e",
  SUPERSEDED: "#6a5a8a",
  BLOCKED: "#9a7d2e",
};
