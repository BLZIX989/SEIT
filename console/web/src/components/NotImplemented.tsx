/**
 * The single, shared "this screen has no backend support yet" panel.
 * Brief section XIII/XXXII: never fake a progress bar or simulate
 * successful execution -- every screen without a real endpoint behind
 * it renders this component instead of stub content that could be
 * mistaken for a working feature.
 */
export function NotImplemented({
  feature,
  reason,
}: {
  feature: string;
  reason: string;
}) {
  return (
    <div className="not-implemented-panel">
      <div className="not-implemented-badge">NOT IMPLEMENTED</div>
      <h3>{feature}</h3>
      <p>{reason}</p>
    </div>
  );
}
