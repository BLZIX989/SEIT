import { useState } from "react";
import { Link } from "react-router-dom";
import { NotImplemented } from "../components/NotImplemented";
import {
  useLiteratureCrosswalk, useLiteratureItems, useLiteratureRecoveries, useLiteratureSources,
} from "../api/queries";

/**
 * Literature Workspace (Phase 9), wired to the existing literature/
 * ingestion architecture -- real acquisition manifests, real extraction
 * registries (two separate, differently-shaped campaigns, kept
 * verbatim), the real MDCL crosswalk, and real proposed recovery
 * records. External literature search (arXiv/web APIs) is explicitly
 * out of scope here -- nothing on this page makes a network call, and
 * that limitation is stated honestly rather than simulated.
 */
export function Literature() {
  const sources = useLiteratureSources();
  const items = useLiteratureItems();
  const crosswalkAll = useLiteratureCrosswalk();
  const recoveries = useLiteratureRecoveries();

  const [corpusFilter, setCorpusFilter] = useState<"" | "string_theory" | "general">("");
  const [search, setSearch] = useState("");
  const [nodeFilter, setNodeFilter] = useState("");

  const filteredItems = (items.data ?? []).filter((it) => {
    if (corpusFilter && it.corpus !== corpusFilter) return false;
    if (search) {
      const haystack = JSON.stringify(it.raw).toLowerCase();
      if (!haystack.includes(search.toLowerCase())) return false;
    }
    return true;
  });

  const crosswalkRows = (crosswalkAll.data ?? []).filter((r) => !nodeFilter || r.mdcl_node_id === nodeFilter);
  const crosswalkNodeIds = Array.from(new Set((crosswalkAll.data ?? []).map((r) => r.mdcl_node_id))).sort();

  return (
    <div>
      <h1>Literature</h1>
      <p className="section-note">
        Real content from the existing literature ingestion campaigns -- acquisition provenance,
        extracted items with page/section/equation citations, the curated MDCL crosswalk, and
        proposed (never canonical) recovery records.
      </p>

      <h2>Acquired sources ({sources.data?.length ?? 0})</h2>
      {sources.data && (
        <table className="data-table">
          <thead><tr><th>Title</th><th>Author</th><th>Pages</th><th>SHA256</th><th>Source</th></tr></thead>
          <tbody>
            {sources.data.map((s) => (
              <tr key={s.SOURCE_ID}>
                <td>{s.TITLE}</td>
                <td>{s.AUTHOR}</td>
                <td>{s.PAGE_COUNT}</td>
                <td><code title={s.SHA256}>{s.SHA256.slice(0, 12)}…</code></td>
                <td><a href={s.SOURCE_URL} target="_blank" rel="noreferrer">{s.PRIMARY_OR_MIRROR}</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2>Extracted items ({filteredItems.length} of {items.data?.length ?? 0})</h2>
      <div className="filter-group" style={{ marginBottom: 10 }}>
        <span className="filter-group__label">Corpus</span>
        <select value={corpusFilter} onChange={(e) => setCorpusFilter(e.target.value as typeof corpusFilter)}>
          <option value="">All</option>
          <option value="string_theory">string_theory</option>
          <option value="general">general</option>
        </select>
        <input
          className="graph-search"
          placeholder="Search extracted content…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      {filteredItems.length > 0 && (
        <table className="data-table">
          <thead><tr><th>ID</th><th>Corpus</th><th>Source</th><th>Topic / object</th></tr></thead>
          <tbody>
            {filteredItems.slice(0, 100).map((it) => (
              <tr key={`${it.corpus}-${it.id}`}>
                <td><code>{it.id}</code></td>
                <td>{it.corpus}</td>
                <td>{it.source_id}</td>
                <td>{String(it.raw.MATHEMATICAL_OBJECT ?? it.raw.EXACT_TOPIC ?? "")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {filteredItems.length > 100 && (
        <p className="section-note">Showing first 100 of {filteredItems.length} matches -- narrow the search to see more.</p>
      )}

      <h2>MDCL crosswalk ({crosswalkRows.length} of {crosswalkAll.data?.length ?? 0})</h2>
      <p className="section-note">
        The one real literature-to-node linkage in this repository: a curated
        <code> MDCL_NODE_ID</code> column, not free-text matching. Rows naming a node the compiler
        doesn't register yet are shown as-is, never hidden or treated as a broken link.
      </p>
      <div className="filter-group" style={{ marginBottom: 10 }}>
        <span className="filter-group__label">Node</span>
        <select value={nodeFilter} onChange={(e) => setNodeFilter(e.target.value)}>
          <option value="">All</option>
          {crosswalkNodeIds.map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
      </div>
      {crosswalkRows.length > 0 && (
        <table className="data-table">
          <thead><tr><th>MDCL node</th><th>Registered?</th><th>Item</th><th>Correspondence</th><th>Status note</th></tr></thead>
          <tbody>
            {crosswalkRows.map((r, i) => (
              <tr key={i}>
                <td>{r.node_is_registered
                  ? <Link to={`/nodes/${encodeURIComponent(r.mdcl_node_id)}`}>{r.mdcl_node_id}</Link>
                  : <code>{r.mdcl_node_id}</code>}
                </td>
                <td>{r.node_is_registered ? "yes" : "no"}</td>
                <td>{r.raw.STRING_ITEM_ID}</td>
                <td>{r.raw.STRUCTURAL_CORRESPONDENCE}</td>
                <td>{r.raw.STATUS}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2>Proposed recoveries ({recoveries.data?.length ?? 0})</h2>
      <p className="section-note">
        &ldquo;Proposed&rdquo; in the name: a recovery attempt's target node and required inputs
        being recorded is not the same as the recovery being complete or canonical.
      </p>
      {recoveries.data && recoveries.data.map((r) => (
        <div key={r.id} className="audit-card">
          <div className="audit-card__header">
            <span className="audit-card__name">{r.id}</span>
            <Link to={`/nodes/${encodeURIComponent(String(r.raw.TARGET_NODE))}`}>{String(r.raw.TARGET_NODE)}</Link>
          </div>
          <p className="section-note" style={{ margin: "6px 0 0" }}>{String(r.raw.REQUIRED_INPUTS ?? "")}</p>
        </div>
      ))}

      <NotImplemented
        feature="External literature search (arXiv / web APIs)"
        reason="Out of scope for this phase (roadmap: 'external search is scoped separately if
          requested') -- nothing on this page makes a network call. Everything above is real,
          already-ingested content from the literature/ directory and its provenance manifests."
      />
    </div>
  );
}
