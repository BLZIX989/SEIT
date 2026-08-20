import { NotImplemented } from "../components/NotImplemented";

export function Literature() {
  return (
    <div>
      <h1>Literature</h1>
      <NotImplemented
        feature="Literature workspace (search / import / extract / map to node / compare / cite /
          reject as irrelevant)"
        reason="Backend required: no /api/literature endpoint exists yet (Phase 9). Real literature
          ingestion content already exists on disk in the repository's literature/ directory
          (STRING_THEORY_LITERATURE_REGISTRY.json, crosswalks, provenance reports from the L0-ST
          campaign) but is not yet wired into the console API."
      />
    </div>
  );
}
