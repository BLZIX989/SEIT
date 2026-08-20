import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Audits } from "./screens/Audits";
import { DependencyGraph } from "./screens/DependencyGraph";
import { DerivationLab } from "./screens/DerivationLab";
import { Execution } from "./screens/Execution";
import { Falsification } from "./screens/Falsification";
import { Hypotheses } from "./screens/Hypotheses";
import { Literature } from "./screens/Literature";
import { Overview } from "./screens/Overview";
import { Proofs } from "./screens/Proofs";
import { Provenance } from "./screens/Provenance";
import { Registries } from "./screens/Registries";
import { Research } from "./screens/Research";
import { Runs } from "./screens/Runs";
import { Settings } from "./screens/Settings";
import { TheoryState } from "./screens/TheoryState";

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="graph" element={<DependencyGraph />} />
        <Route path="theory-state" element={<TheoryState />} />
        <Route path="derivation-lab" element={<DerivationLab />} />
        <Route path="research" element={<Research />} />
        <Route path="hypotheses" element={<Hypotheses />} />
        <Route path="execution" element={<Execution />} />
        <Route path="proofs" element={<Proofs />} />
        <Route path="falsification" element={<Falsification />} />
        <Route path="literature" element={<Literature />} />
        <Route path="provenance" element={<Provenance />} />
        <Route path="audits" element={<Audits />} />
        <Route path="runs" element={<Runs />} />
        <Route path="registries" element={<Registries />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
