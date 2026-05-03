export default function AbstainCallout({ rationale }: { rationale: string }) {
  const reasons = rationale
    .replace(/^Abstained:\s*/i, "")
    .replace(/\.$/, "")
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean);

  return (
    <div
      className="rounded-xl border border-verdict-unknown-ring bg-verdict-unknown-bg p-4"
      data-testid="abstain-callout"
    >
      <div className="flex items-center gap-2">
        <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4 text-verdict-unknown" aria-hidden>
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.94 6.94A1.5 1.5 0 0110 6.5a1.5 1.5 0 011.06 2.56l-.78.78a1.5 1.5 0 00-.44 1.06v.6a.75.75 0 01-1.5 0v-.6c0-.8.32-1.56.88-2.12l.78-.78a.75.75 0 00-1.06-1.06zM10 13.75A.75.75 0 1010 15a.75.75 0 000-1.25z" clipRule="evenodd" />
        </svg>
        <p className="font-display text-sm font-semibold text-verdict-unknown">
          Why we abstained
        </p>
      </div>
      <ul className="mt-2 list-disc space-y-0.5 pl-5 text-sm text-verdict-unknown">
        {reasons.length > 0 ? (
          reasons.map((r, i) => <li key={i}>{r}</li>)
        ) : (
          <li>{rationale}</li>
        )}
      </ul>
    </div>
  );
}
