import { useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  useCreateHypothesis, useHypotheses, useHypothesis, useNodes, useTransitionHypothesis,
} from "../api/queries";
import type { HypothesisStatus, PossibleDuplicate } from "../api/types";
import { ALLOWED_TRANSITIONS, HYPOTHESIS_STATUS_COLORS } from "../hypotheses/hypothesisStatus";

function HypothesisBadge({ status }: { status: HypothesisStatus }) {
  return (
    <span className="status-badge" style={{ backgroundColor: HYPOTHESIS_STATUS_COLORS[status] }}>
      {status}
    </span>
  );
}

/**
 * The persistent Hypothesis Engine (brief section XI, Phase 7). Every
 * hypothesis is real, stored append-only in
 * console_research/hypotheses.jsonl -- never edited in place, never
 * touching a canonical registry, and its status can never promote the
 * MDCL node it targets (that only ever happens via a real compiler
 * run, Phase 6). This screen directly answers "what have we already
 * tried for this node, and why did it fail" -- the brief's stated goal
 * for the engine.
 */
export function Hypotheses() {
  const nodes = useNodes();
  const [nodeFilter, setNodeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const hypotheses = useHypotheses({
    target_node_id: nodeFilter || undefined,
    status: statusFilter || undefined,
  });
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [statement, setStatement] = useState("");
  const [targetNode, setTargetNode] = useState("");
  const [assumptions, setAssumptions] = useState("");
  const [duplicates, setDuplicates] = useState<PossibleDuplicate[]>([]);
  const createHyp = useCreateHypothesis();

  const submitCreate = (e: FormEvent) => {
    e.preventDefault();
    if (!statement.trim() || !targetNode) return;
    createHyp.mutate(
      {
        statement: statement.trim(),
        target_node_id: targetNode,
        assumptions: assumptions.split(",").map((a) => a.trim()).filter(Boolean),
      },
      {
        onSuccess: (data) => {
          setDuplicates(data.possible_duplicates);
          setSelectedId(data.hypothesis.id);
          setStatement("");
          setAssumptions("");
        },
      },
    );
  };

  return (
    <div>
      <h1>Hypotheses</h1>
      <p className="section-note">
        Persistent, append-only hypothesis registry (<code>console_research/hypotheses.jsonl</code>).
        A hypothesis's status is informational only -- nothing here can promote the MDCL node it
        targets; only a real compiler run can do that (see Execution Console).
      </p>

      <h2>Propose a hypothesis</h2>
      <form onSubmit={submitCreate} className="hypothesis-form">
        <label>
          Target node
          <select value={targetNode} onChange={(e) => setTargetNode(e.target.value)} required>
            <option value="">Select a node…</option>
            {(nodes.data ?? []).map((n) => (
              <option key={n.id} value={n.id}>{n.id} ({n.status})</option>
            ))}
          </select>
        </label>
        <label>
          Statement
          <textarea
            value={statement}
            onChange={(e) => setStatement(e.target.value)}
            placeholder="What are you proposing about this node, and why?"
            rows={3}
            required
          />
        </label>
        <label>
          Assumptions (comma-separated)
          <input value={assumptions} onChange={(e) => setAssumptions(e.target.value)} placeholder="e.g. graph is connected, N > 50" />
        </label>
        <button className="link-button" type="submit" disabled={createHyp.isPending} style={{ alignSelf: "flex-start", padding: "6px 14px" }}>
          {createHyp.isPending ? "Proposing…" : "Propose hypothesis"}
        </button>
        {createHyp.isError && <div className="error-panel">{String(createHyp.error)}</div>}
      </form>

      {duplicates.length > 0 && (
        <div className="duplicate-warning">
          <strong>Possible duplicate{duplicates.length > 1 ? "s" : ""} (heuristic match, not certain):</strong>
          <ul>
            {duplicates.map((d) => (
              <li key={d.id}>
                <button className="link-button" onClick={() => setSelectedId(d.id)}>{d.id}</button>{" "}
                ({d.match_confidence}, similarity {d.similarity}) -- <HypothesisBadge status={d.status as HypothesisStatus} /> &ldquo;{d.statement}&rdquo;
              </li>
            ))}
          </ul>
        </div>
      )}

      <h2>All hypotheses</h2>
      <div className="filter-group" style={{ marginBottom: 10 }}>
        <span className="filter-group__label">Node</span>
        <select value={nodeFilter} onChange={(e) => setNodeFilter(e.target.value)}>
          <option value="">All</option>
          {(nodes.data ?? []).map((n) => <option key={n.id} value={n.id}>{n.id}</option>)}
        </select>
        <span className="filter-group__label">Status</span>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All</option>
          {Object.keys(HYPOTHESIS_STATUS_COLORS).map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {hypotheses.data && hypotheses.data.length === 0 && (
        <p className="section-note">No hypotheses yet -- propose one above.</p>
      )}
      {hypotheses.data && hypotheses.data.length > 0 && (
        <table className="data-table">
          <thead><tr><th>ID</th><th>Target</th><th>Status</th><th>Statement</th><th>Updated</th></tr></thead>
          <tbody>
            {hypotheses.data.map((h) => (
              <tr key={h.id} className={h.id === selectedId ? "row--frontier" : undefined} style={{ cursor: "pointer" }} onClick={() => setSelectedId(h.id)}>
                <td><code>{h.id}</code></td>
                <td><Link to={`/nodes/${encodeURIComponent(h.target_node_id)}`} onClick={(e) => e.stopPropagation()}>{h.target_node_id}</Link></td>
                <td><HypothesisBadge status={h.status} /></td>
                <td>{h.statement}</td>
                <td>{h.updated_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selectedId && <HypothesisDetailPanel id={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  );
}

function HypothesisDetailPanel({ id, onClose }: { id: string; onClose: () => void }) {
  const detail = useHypothesis(id);
  const transition = useTransitionHypothesis();
  const [reason, setReason] = useState("");
  const [pendingStatus, setPendingStatus] = useState<HypothesisStatus | null>(null);

  if (detail.isLoading) return <p>Loading…</p>;
  if (!detail.data) return null;
  const { current, history } = detail.data;
  const nextStates = ALLOWED_TRANSITIONS[current.status] ?? [];

  const submitTransition = (e: FormEvent) => {
    e.preventDefault();
    if (!pendingStatus || !reason.trim()) return;
    transition.mutate(
      { id, req: { new_status: pendingStatus, reason: reason.trim() } },
      { onSuccess: () => { setReason(""); setPendingStatus(null); } },
    );
  };

  return (
    <div className="node-detail-panel" style={{ width: "auto", maxWidth: 760 }}>
      <div className="node-detail-panel__header">
        <h3><code>{current.id}</code></h3>
        <button className="btn-close" onClick={onClose} aria-label="Close">×</button>
      </div>

      <div className="node-detail-panel__meta">
        <HypothesisBadge status={current.status} />
        <Link className="link-button" to={`/nodes/${encodeURIComponent(current.target_node_id)}`}>
          target: {current.target_node_id}
        </Link>
      </div>

      <p>{current.statement}</p>

      <h4>Assumptions ({current.assumptions.length})</h4>
      <p className="section-note">{current.assumptions.join(", ") || "None recorded."}</p>

      <h4>Evidence ({current.evidence.length})</h4>
      {current.evidence.length === 0 && <p className="section-note">None recorded.</p>}
      {current.evidence.map((e, i) => (
        <p key={i} className="section-note">{e.kind}: {e.description}{e.ref_id ? ` (${e.ref_id})` : ""}</p>
      ))}

      <h4>Full history ({history.length} state{history.length === 1 ? "" : "s"})</h4>
      <table className="data-table">
        <thead><tr><th>When</th><th>Status</th><th>Reason</th></tr></thead>
        <tbody>
          {history.map((h, i) => (
            <tr key={i}>
              <td>{h.updated_at}</td>
              <td><HypothesisBadge status={h.status} /></td>
              <td>{String(h.provenance.last_transition_reason ?? (i === 0 ? "proposed" : "—"))}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {nextStates.length === 0 ? (
        <p className="section-note">Terminal status -- no further transitions.</p>
      ) : (
        <form onSubmit={submitTransition} className="hypothesis-form" style={{ marginTop: 10 }}>
          <h4 style={{ margin: "0 0 4px" }}>Transition</h4>
          <div className="filter-group">
            {nextStates.map((s) => (
              <label key={s} className={`filter-chip${pendingStatus === s ? " filter-chip--active" : ""}`}>
                <input type="radio" name="next-status" style={{ display: "none" }} checked={pendingStatus === s} onChange={() => setPendingStatus(s)} />
                {s}
              </label>
            ))}
          </div>
          <label>
            Reason
            <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Why this transition?" required />
          </label>
          <button className="link-button" type="submit" disabled={!pendingStatus || transition.isPending} style={{ alignSelf: "flex-start", padding: "6px 14px" }}>
            {transition.isPending ? "Recording…" : "Record transition"}
          </button>
          {transition.isError && <div className="error-panel">{String(transition.error)}</div>}
        </form>
      )}
    </div>
  );
}
