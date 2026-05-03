import type { VerifyResponse } from "@/lib/types";
import AbstainCallout from "./AbstainCallout";
import ConfidenceDial from "./ConfidenceDial";
import EvidenceList from "./EvidenceList";
import Markdown from "./Markdown";
import VerdictChip from "./VerdictChip";
import Card from "./ui/Card";
import Badge from "./ui/Badge";

export default function VerdictCard({ response }: { response: VerifyResponse }) {
  return (
    <Card className="overflow-hidden" data-testid="verdict-card">
      <div className="flex flex-col gap-6 p-6 sm:flex-row sm:items-start">
        <div className="flex shrink-0 flex-col items-center gap-3">
          <ConfidenceDial value={response.confidence} />
          {response.low_confidence && (
            <Badge tone="unknown" data-testid="low-conf-flag">
              <svg viewBox="0 0 20 20" fill="currentColor" className="h-3 w-3" aria-hidden>
                <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 6a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 6zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
              low confidence
            </Badge>
          )}
        </div>
        <div className="flex-1 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <VerdictChip verdict={response.verdict} />
            <span className="ml-auto text-[10px] font-mono uppercase tracking-wider text-ink-muted">
              {response.latency_ms.toFixed(0)} ms · {response.metadata.model_id}
            </span>
          </div>
          {response.verdict === "Abstain" ? (
            <AbstainCallout rationale={response.rationale} />
          ) : (
            <div>
              <h3 className="font-display text-sm font-semibold text-ink">
                Rationale
              </h3>
              <Markdown className="mt-1">{response.rationale}</Markdown>
            </div>
          )}
        </div>
      </div>

      <div className="border-t border-border bg-muted/40 p-6">
        <EvidenceList evidence={response.evidence} />
      </div>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-border px-6 py-3 font-mono text-[10px] text-ink-muted">
        <span>id {response.request_id.slice(0, 8)}</span>
        {response.metadata.langfuse_trace_id && (
          <span>trace {response.metadata.langfuse_trace_id.slice(0, 8)}</span>
        )}
        <span className="ml-auto rounded-full bg-muted px-2 py-0.5">
          {response.disclosure}
        </span>
      </div>
    </Card>
  );
}
