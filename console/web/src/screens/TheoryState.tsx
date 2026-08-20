import { NotImplemented } from "../components/NotImplemented";
import { ChainlinkView } from "../graph/ChainlinkView";
import { useMdcl, useStateRollup } from "../api/queries";

/**
 * Brief section VIII's formal Theory State object T_t = (P,O,E,D,C,F,V,R).
 * This screen maps what is ACTUALLY available today onto that tuple and
 * is explicit about the two components (C: closed/admissible set beyond
 * the live frontier snapshot, R: research state) that have no backend
 * yet -- it does not synthesize placeholder values for them.
 */
export function TheoryState() {
  const mdcl = useMdcl();
  const state = useStateRollup();

  const objects = (mdcl.data?.objects as unknown[] | undefined)?.length ?? null;
  const equations = (mdcl.data?.equations as unknown[] | undefined)?.length ?? null;
  const transformations = (mdcl.data?.transformations as unknown[] | undefined)?.length ?? null;
  const types = (mdcl.data?.types as unknown[] | undefined)?.length ?? null;

  return (
    <div>
      <h1>Theory State</h1>
      <p className="section-note">
        T_t = (P, O, E, D, C, F, V, R) -- current mapping onto the live master_mdcl.json:
      </p>
      <table className="data-table">
        <thead>
          <tr><th>Component</th><th>Meaning</th><th>Current value</th></tr>
        </thead>
        <tbody>
          <tr><td>P</td><td>primitives (types)</td><td>{types ?? "…"}</td></tr>
          <tr><td>O</td><td>operators/objects</td><td>{objects ?? "…"}</td></tr>
          <tr><td>E</td><td>equations</td><td>{equations ?? "…"}</td></tr>
          <tr><td>D</td><td>dependency DAG</td><td>{transformations !== null && objects !== null && equations !== null ? `${transformations + objects + equations} nodes` : "…"}</td></tr>
          <tr><td>C</td><td>closed/admissible set</td><td>{state.data ? `${(state.data.by_status.VERIFIED ?? 0) + (state.data.by_status.DERIVED ?? 0) + (state.data.by_status.CALCULATED ?? 0) + (state.data.by_status.CONDITIONAL ?? 0)}` : "…"}</td></tr>
          <tr><td>F</td><td>failed/falsified set</td><td>{state.data ? `${(state.data.by_status.FAIL ?? 0) + (state.data.by_status.FALSIFIED ?? 0)}` : "…"}</td></tr>
          <tr><td>V</td><td>verification evidence</td><td>see Proofs / Falsification screens</td></tr>
          <tr><td>R</td><td>research state</td><td>NOT IMPLEMENTED (see below)</td></tr>
        </tbody>
      </table>

      <h2>Master Chainlink (brief section XXIV)</h2>
      <p className="section-note">
        Rendered from the real compiler/ir/forward_chain.py template chain -- not a separate,
        hand-maintained view. Click any arrow for its full detail (status, DER ID, proof,
        assumptions, calculation, dependencies, literature, failures, open obligations).
      </p>
      <ChainlinkView />

      <NotImplemented
        feature="T₀ → T₁ → T₂ → … state evolution history"
        reason="No run/snapshot store exists yet (Phase 6 of the plan). Today's registry files are
          overwritten in place by each `run_compiler.py` invocation -- there is exactly one Theory
          State snapshot on disk at any time, not a history of them, so this view cannot show
          'what changed' between runs until console_runs/ snapshotting is implemented."
      />
    </div>
  );
}
