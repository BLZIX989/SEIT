import { NotImplemented } from "../components/NotImplemented";

export function Research() {
  return (
    <div>
      <h1>Research</h1>
      <NotImplemented
        feature="Research orchestration (literature search, candidate generation, evidence
          classification)"
        reason="Backend required: the Research Orchestrator (brief section X) is net-new and has
          no implementation yet -- Phase 7 of the plan. Nothing in the compiler contradicts
          building it, but nothing provides even a partial version today."
      />
    </div>
  );
}
