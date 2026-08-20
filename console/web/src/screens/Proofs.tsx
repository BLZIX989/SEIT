import { NotImplemented } from "../components/NotImplemented";

export function Proofs() {
  return (
    <div>
      <h1>Proofs</h1>
      <NotImplemented
        feature="Proof workspace (hypotheses / lemma dependencies / derivation / conclusion /
          verification / counterexamples / circular-dependency detection)"
        reason="Backend required: there is no dedicated /api/proofs endpoint yet (Phase 8). The
          real proof_registry.json (currently 6 verified entries) is visible today only per-node
          via /api/nodes/:id, where each transformation's proof text and status are shown
          verbatim -- a standalone proof-workspace listing/detail view is not yet built."
      />
    </div>
  );
}
