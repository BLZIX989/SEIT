import { NavLink, Outlet } from "react-router-dom";
import { useHealth } from "../api/queries";

// The 15 primary-nav items, brief section V, verbatim order.
const NAV_ITEMS: { path: string; label: string }[] = [
  { path: "/", label: "Overview" },
  { path: "/graph", label: "Dependency Graph" },
  { path: "/theory-state", label: "Theory State" },
  { path: "/derivation-lab", label: "Derivation Lab" },
  { path: "/research", label: "Research" },
  { path: "/hypotheses", label: "Hypotheses" },
  { path: "/execution", label: "Execution" },
  { path: "/proofs", label: "Proofs" },
  { path: "/falsification", label: "Falsification" },
  { path: "/literature", label: "Literature" },
  { path: "/provenance", label: "Provenance" },
  { path: "/audits", label: "Audits" },
  { path: "/runs", label: "Runs" },
  { path: "/registries", label: "Registries" },
  { path: "/settings", label: "Settings" },
];

export function Layout() {
  const health = useHealth();

  return (
    <div className="console-shell">
      <header className="console-topbar">
        <div className="console-topbar__brand">
          <span className="console-topbar__title">UOC Research Console</span>
          <span className="console-topbar__subtitle">Universal Organizational Compiler</span>
        </div>
        <div className="console-topbar__status">
          {health.isLoading && <span className="api-status api-status--pending">API…</span>}
          {health.isError && <span className="api-status api-status--down">API unreachable</span>}
          {health.data && (
            <span className="api-status api-status--up">
              API up · phase {health.data.phase}
            </span>
          )}
        </div>
      </header>
      <div className="console-body">
        <nav className="console-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                "console-nav__item" + (isActive ? " console-nav__item--active" : "")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <main className="console-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
