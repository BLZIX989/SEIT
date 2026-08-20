import { StatusBadge } from "../components/StatusBadge";
import { useAudits } from "../api/queries";

/**
 * Real data end to end: compiler/verification/self_audit.py ->
 * self_audit_report.json -> /api/audits -> here. This is the multi-
 * auditor concept (brief section XVI) as it exists TODAY -- the 10
 * self-audits, each independent, each reported without a shared
 * "conclusion" being imposed across them. The 8-persona framing
 * (Dependency/Consistency/Proof/Falsification/Literature/Numerical/
 * Compiler/Status auditors) from the brief is a Phase 8+ UI
 * reorganization of this same real data, not yet built.
 */
export function Audits() {
  const audits = useAudits();

  if (audits.isLoading) return <p>Loading audit results…</p>;
  if (audits.isError) return <p className="error-panel">Could not load /api/audits: {String(audits.error)}</p>;

  return (
    <div>
      <h1>Audits</h1>
      <p className="section-note">
        {audits.data!.length} independent self-audits, from compiler/verification/self_audit.py.
        No auditor here may silently modify canonical state -- these are pure read-only checks.
      </p>
      {audits.data!.map((a) => (
        <div key={a.name} className="audit-card">
          <div className="audit-card__header">
            <span className="audit-card__name">{a.name}</span>
            <StatusBadge status={a.passed ? "VERIFIED" : "FAIL"} />
          </div>
          {a.issues.length > 0 && (
            <ul className="audit-card__issues">
              {a.issues.map((issue, i) => <li key={i}>{issue}</li>)}
            </ul>
          )}
          {Object.keys(a.details).length > 0 && (
            <pre className="audit-card__details">{JSON.stringify(a.details, null, 2)}</pre>
          )}
        </div>
      ))}
    </div>
  );
}
