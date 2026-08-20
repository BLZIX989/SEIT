import { useAudits, useFc005, useMdcl, useStateRollup } from "../api/queries";

/**
 * Real data: a direct index over the registry files the compiler
 * writes, per UOC_RESEARCH_CONSOLE_ARCHITECTURE.md section 5's
 * canonical-adapter mapping table.
 */
export function Registries() {
  const mdcl = useMdcl();
  const state = useStateRollup();
  const audits = useAudits();
  const fc005 = useFc005();

  const rows: { file: string; description: string; count: string | number }[] = [
    { file: "type_registry.json", description: "Type definitions", count: (mdcl.data?.types as unknown[] | undefined)?.length ?? "…" },
    { file: "object_registry.json", description: "Object nodes", count: state.data?.by_kind.Object ?? "…" },
    { file: "transformation_registry.json", description: "Transformation nodes", count: state.data?.by_kind.Transformation ?? "…" },
    { file: "equation_registry.json", description: "Equation nodes", count: state.data?.by_kind.Equation ?? "…" },
    { file: "status_matrix.json", description: "Flattened id/kind/status/dependencies", count: state.data?.total_nodes ?? "…" },
    { file: "master_mdcl.json", description: "Full MDCL (types+objects+transformations+equations+status_matrix)", count: "1 document" },
    { file: "self_audit_report.json", description: "Self-audit results", count: audits.data?.length ?? "…" },
    { file: "fc005_result.json", description: "FC-005 stage-gate summary", count: fc005.data?.terminal_status ?? "…" },
  ];

  return (
    <div>
      <h1>Registries</h1>
      <p className="section-note">
        Direct index over the canonical registry files at the repository root. These are the ONLY
        source of truth (brief section IV) -- this screen reads them, it does not duplicate or
        cache a second copy of them anywhere persistent.
      </p>
      <table className="data-table">
        <thead><tr><th>File</th><th>Contents</th><th>Count</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.file}>
              <td><code>{r.file}</code></td>
              <td>{r.description}</td>
              <td>{r.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="section-note">
        proof_registry.json, calculation_registry.json, falsification_registry.json, and
        provenance_registry.json are also served by the API (via /api/nodes/:id's cross-references)
        but have no standalone listing endpoint yet -- see the Proofs/Falsification/Provenance
        screens.
      </p>

      <h2>FC-005 (brief section XXII)</h2>
      <p className="section-note">
        Exposed exactly as the compiler reports it -- this panel never implies DESI closure while
        fc005_result.json itself reports failure/retriable/open.
      </p>
      {fc005.data && (
        <table className="data-table">
          <tbody>
            <tr><td>Terminal status</td><td>{String(fc005.data.terminal_status)}</td></tr>
            <tr><td>All self-audits passed</td><td>{String(fc005.data.all_self_audits_passed ?? "unknown")}</td></tr>
          </tbody>
        </table>
      )}
    </div>
  );
}
