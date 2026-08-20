import { NotImplemented } from "../components/NotImplemented";

export function Falsification() {
  return (
    <div>
      <h1>Falsification</h1>
      <NotImplemented
        feature="Falsification workspace (WHAT WOULD FALSIFY THIS? / executable test list)"
        reason="Backend required: no dedicated /api/falsifications endpoint yet (Phase 8). The
          real falsification_registry.json entries are visible today only per-node via
          /api/nodes/:id (with an honest match-confidence label, since falsification records
          store a free-text target rather than a strict node-id foreign key) -- a standalone
          workspace listing every falsification protocol and its executable test is not yet
          built. compiler/falsification/protocols.py already implements 4 real protocols
          (structural elimination, representation invariance, mathematical invariance,
          observer-independent structural reduction) this workspace will eventually expose."
      />
    </div>
  );
}
