import { NotImplemented } from "../components/NotImplemented";

export function Hypotheses() {
  return (
    <div>
      <h1>Hypotheses</h1>
      <NotImplemented
        feature="Persistent hypothesis engine (WRITE/MERGE/RECALL/RESOLVE/REJECT/SUPERSEDE)"
        reason="Backend required: console_research/hypotheses.jsonl and its API (brief section XI;
          UOC_RESEARCH_CONSOLE_ARCHITECTURE.md section 4.4) are specified but not built yet --
          Phase 7. The closest existing analogue is compiler/ir/toe_closure_hypotheses.py's four
          hard-coded H1-H4 functions, which are real but not a general, persistent hypothesis
          registry the UI can read from."
      />
    </div>
  );
}
