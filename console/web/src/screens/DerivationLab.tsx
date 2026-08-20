import { NotImplemented } from "../components/NotImplemented";

export function DerivationLab() {
  return (
    <div>
      <h1>Derivation Lab</h1>
      <NotImplemented
        feature="Chainlink derivation workspace (RUN DERIVATION / SEARCH LITERATURE / GENERATE
          CANDIDATE / PROVE / FALSIFY / COMPARE / EXECUTE NUMERICALLY / REGISTER / REJECT)"
        reason="Backend required: none of these actions have a compiler-side execution endpoint
          yet (brief section IX; Phase 6/7 of the implementation plan). See the Theory State
          screen's chainlink table for the read-only equivalent of this screen's
          INPUT/OUTPUT/DEPENDENCIES panels, available today via /api/chainlink."
      />
    </div>
  );
}
