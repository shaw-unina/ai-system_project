// Parses the FR-8 rationale ("Abstained: a; b; c.") into a bulleted reason list.
interface Props {
  rationale: string;
}

export default function AbstainCallout({ rationale }: Props) {
  const reasons = rationale
    .replace(/^Abstained:\s*/i, "")
    .replace(/\.$/, "")
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean);

  return (
    <div className="border-l-4 border-amber-500 bg-amber-50 p-3" data-testid="abstain-callout">
      <p className="font-semibold text-amber-900">Why we abstained</p>
      <ul className="list-disc list-inside text-sm text-amber-900">
        {reasons.length > 0 ? (
          reasons.map((r, i) => <li key={i}>{r}</li>)
        ) : (
          <li>{rationale}</li>
        )}
      </ul>
    </div>
  );
}
