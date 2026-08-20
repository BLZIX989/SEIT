import { NotImplemented } from "../components/NotImplemented";

export function Provenance() {
  return (
    <div>
      <h1>Provenance</h1>
      <NotImplemented
        feature="Standalone provenance browser (origin classification: DERIVED / CALCULATED /
          VERIFIED / EXTERNAL / LITERATURE / USER-SUPPLIED / PROPOSED / SYNTHETIC CONTROL /
          OBSERVATIONAL DATA)"
        reason="Backend required: no dedicated /api/provenance listing endpoint yet (Phase 8/9).
          The real provenance_registry.json (105 entries, one per node, with source, git commit,
          code version, and numerical environment) is visible today per-node via /api/nodes/:id."
      />
    </div>
  );
}
