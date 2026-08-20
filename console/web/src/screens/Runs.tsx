import { NotImplemented } from "../components/NotImplemented";

export function Runs() {
  return (
    <div>
      <h1>Runs</h1>
      <NotImplemented
        feature="Run history and comparison (RUN 001 vs RUN 002 vs RUN 003)"
        reason="Backend required: console_runs/ snapshot storage does not exist yet (Phase 6/10).
          There is currently no run/session concept anywhere in the compiler -- each
          `run_compiler.py` invocation overwrites the same registry files in place, so there is
          exactly one state on disk at any time, not a history of runs to list or diff."
      />
    </div>
  );
}
