import type { VerifyResponse } from "@/lib/types";
import AbstainCallout from "./AbstainCallout";
import ConfidenceMeter from "./ConfidenceMeter";
import EvidenceList from "./EvidenceList";

interface Props {
  response: VerifyResponse;
}

const VERDICT_TINT: Record<string, string> = {
  Supported: "bg-emerald-100 text-emerald-900",
  Refuted: "bg-rose-100 text-rose-900",
  NotEnoughEvidence: "bg-slate-100 text-slate-900",
  Abstain: "bg-amber-100 text-amber-900",
};

export default function VerdictCard({ response }: Props) {
  const tint = VERDICT_TINT[response.verdict] ?? "bg-slate-100 text-slate-900";
  return (
    <article
      className="rounded-lg border border-slate-200 bg-white p-5 space-y-4 shadow-sm"
      data-testid="verdict-card"
    >
      <header className="flex items-center gap-3">
        <span className={`px-2 py-1 rounded text-sm font-semibold ${tint}`} data-testid="verdict-label">
          {response.verdict}
        </span>
        {response.low_confidence && (
          <span
            className="px-2 py-1 rounded bg-amber-200 text-amber-900 text-xs font-medium"
            data-testid="low-conf-flag"
          >
            ⚠ low confidence
          </span>
        )}
        <span className="text-xs uppercase tracking-wide text-slate-400 ml-auto">
          {response.disclosure}
        </span>
      </header>

      <ConfidenceMeter value={response.confidence} />

      {response.verdict === "Abstain" ? (
        <AbstainCallout rationale={response.rationale} />
      ) : (
        <p className="text-sm text-slate-700">
          <span className="font-semibold">Rationale:</span> {response.rationale}
        </p>
      )}

      <section>
        <h3 className="text-sm font-semibold text-slate-700 mb-1">
          Evidence ({response.evidence.length})
        </h3>
        <EvidenceList evidence={response.evidence} />
      </section>

      <footer className="text-xs text-slate-400 font-mono flex flex-wrap gap-3">
        <span>request_id: {response.request_id}</span>
        {response.metadata.langfuse_trace_id && (
          <span>trace: {response.metadata.langfuse_trace_id}</span>
        )}
        <span>latency: {response.latency_ms.toFixed(0)} ms</span>
        <span>model: {response.metadata.model_id}</span>
      </footer>
    </article>
  );
}
