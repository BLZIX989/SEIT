import { useState } from "react";
import { Link } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import type { ChainlinkArrow } from "../api/types";
import { useChainlink } from "../api/queries";

/**
 * Interactive Master Chainlink View (brief section XXIV): each arrow
 * of the real compiler/ir/forward_chain.py TEMPLATE_CHAIN is clickable
 * and opens a detail panel with STATUS / DER ID / PROOF / ASSUMPTIONS /
 * CALCULATION / DEPENDENCIES / LITERATURE / FAILURES / OPEN OBLIGATIONS
 * -- every field sourced from GET /api/chainlink, which is itself built
 * from the real registries (see console/api/canonical/chainlink.py).
 * Fields with no honest backend link (DER ID, LITERATURE) show their
 * explanatory NOT_IMPLEMENTED note rather than a guess.
 */
export function ChainlinkView() {
  const chainlink = useChainlink();
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  if (chainlink.isLoading) return <p>Loading chainlink…</p>;
  if (chainlink.isError) return <div className="error-panel">Failed to load chainlink: {String(chainlink.error)}</div>;
  if (!chainlink.data) return null;

  const arrows = chainlink.data.arrows;
  const selected = selectedIdx !== null ? arrows[selectedIdx] : null;

  return (
    <div className="chainlink-view">
      <div className="chainlink-strip">
        {arrows.map((a, i) => (
          <button
            key={`${a.from_id}->${a.to_id}`}
            className={`chainlink-arrow-chip${selectedIdx === i ? " chainlink-arrow-chip--selected" : ""}`}
            onClick={() => setSelectedIdx(selectedIdx === i ? null : i)}
          >
            <span className="chainlink-arrow-chip__symbol">{a.from_symbol}</span>
            <span className="chainlink-arrow-chip__glyph">→</span>
            <span className="chainlink-arrow-chip__symbol">{a.to_symbol}</span>
            <StatusBadge status={a.status} />
          </button>
        ))}
      </div>
      <p className="section-note">{chainlink.data.note}</p>

      {selected && <ArrowDetail arrow={selected} onClose={() => setSelectedIdx(null)} />}
    </div>
  );
}

function ArrowDetail({ arrow, onClose }: { arrow: ChainlinkArrow; onClose: () => void }) {
  return (
    <div className="chainlink-arrow-detail">
      <div className="node-detail-panel__header">
        <h3>
          {arrow.from_symbol} <code>{arrow.from_id}</code> → {arrow.to_symbol} <code>{arrow.to_id}</code>
        </h3>
        <button className="btn-close" onClick={onClose} aria-label="Close arrow detail">×</button>
      </div>

      <table className="data-table">
        <tbody>
          <tr>
            <td>Status</td>
            <td><StatusBadge status={arrow.status} /></td>
          </tr>
          <tr>
            <td>Execution</td>
            <td>{arrow.execution_status === "NOT_IMPLEMENTED"
              ? <span className="tag tag--not-implemented">NOT IMPLEMENTED</span>
              : <span className="tag tag--executed">EXECUTED</span>}
            </td>
          </tr>
          <tr>
            <td>DER ID</td>
            <td>{arrow.der_id ?? <span className="section-note" style={{ margin: 0 }}>{arrow.der_id_note}</span>}</td>
          </tr>
        </tbody>
      </table>

      <h4>Dependencies ({arrow.dependencies.length})</h4>
      {arrow.dependencies.length === 0 && <p className="section-note">None declared.</p>}
      <ul className="node-ref-list">
        {arrow.dependencies.map((d) => (
          <li key={d}><Link className="link-button" to={`/nodes/${encodeURIComponent(d)}`}>{d}</Link></li>
        ))}
      </ul>

      <h4>Open obligations ({arrow.open_obligations.length})</h4>
      {arrow.open_obligations.length === 0
        ? <p className="section-note">None -- every declared dependency is already in the admissible/closed set.</p>
        : (
          <ul className="node-ref-list">
            {arrow.open_obligations.map((d) => (
              <li key={d}><Link className="link-button" to={`/nodes/${encodeURIComponent(d)}`}>{d}</Link></li>
            ))}
          </ul>
        )}

      <h4>Assumptions ({arrow.assumptions.length})</h4>
      {arrow.assumptions.length === 0 && <p className="section-note">None recorded.</p>}
      {arrow.assumptions.length > 0 && (
        <ul>{arrow.assumptions.map((a, i) => <li key={i}>{a}</li>)}</ul>
      )}

      <h4>Proof ({arrow.proof.length})</h4>
      {arrow.proof.length === 0 && <p className="section-note">No proof record for this node.</p>}
      {arrow.proof.length > 0 && <pre className="audit-card__details">{JSON.stringify(arrow.proof, null, 2)}</pre>}

      <h4>Calculation ({arrow.calculations.length})</h4>
      {arrow.calculations.length === 0 && <p className="section-note">No linked calculation.</p>}
      {arrow.calculations.length > 0 && <pre className="audit-card__details">{JSON.stringify(arrow.calculations, null, 2)}</pre>}

      <h4>Failures ({arrow.failures.length})</h4>
      {arrow.failures.length === 0 && <p className="section-note">No falsification record text-matches this node.</p>}
      {arrow.failures.map((f, i) => (
        <div key={i} className="audit-card">
          <div className="audit-card__header"><span className="tag">{f.match_confidence}</span></div>
          <pre className="audit-card__details">{JSON.stringify(f.record, null, 2)}</pre>
        </div>
      ))}

      <h4>Literature ({arrow.literature.length})</h4>
      <p className="section-note">{arrow.literature_note}</p>
      {arrow.literature.length > 0 && (
        <pre className="audit-card__details">{JSON.stringify(arrow.literature, null, 2)}</pre>
      )}

      <Link className="link-button" to={`/nodes/${encodeURIComponent(arrow.to_id)}`}>Open {arrow.to_id} in Node Inspector ↗</Link>
    </div>
  );
}
