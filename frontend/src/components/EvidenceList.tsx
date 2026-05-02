import type { EvidenceRef } from "@/lib/types";

interface Props {
  evidence: EvidenceRef[];
}

export default function EvidenceList({ evidence }: Props) {
  if (evidence.length === 0) {
    return <p className="text-sm text-slate-500 italic">No evidence retrieved.</p>;
  }
  return (
    <ol className="space-y-2" data-testid="evidence-list">
      {evidence.map((e, i) => (
        <li key={`${e.source_id}-${i}`} className="text-sm">
          <span className="font-mono text-xs text-slate-500">[{e.source_id}]</span>{" "}
          <span className="text-slate-800">{e.span}</span>
          {e.url && (
            <>
              {" "}
              <a
                className="text-blue-600 underline"
                href={e.url}
                target="_blank"
                rel="noreferrer noopener"
              >
                source
              </a>
            </>
          )}
        </li>
      ))}
    </ol>
  );
}
