// NFR-Trans-2: every page mounts this banner via app/layout.tsx.
export default function DisclosureBanner() {
  return (
    <div
      role="alert"
      className="bg-amber-100 border-b border-amber-300 text-amber-900 text-sm py-2 px-4 text-center"
      data-testid="disclosure-banner"
    >
      ⚠️ Outputs are <strong>AI-generated</strong>. Review the evidence and
      rationale before acting on a verdict.
    </div>
  );
}
