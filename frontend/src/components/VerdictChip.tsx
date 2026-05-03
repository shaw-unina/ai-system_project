import type { ReactElement } from "react";
import { CheckCircle2, XCircle, HelpCircle, MinusCircle } from "lucide-react";
import type { VerdictLabel } from "@/lib/types";
import Badge from "@/components/ui/Badge";

const ICONS: Record<VerdictLabel, ReactElement> = {
  Supported: <CheckCircle2 className="h-3.5 w-3.5" aria-hidden />,
  Refuted: <XCircle className="h-3.5 w-3.5" aria-hidden />,
  NotEnoughEvidence: <HelpCircle className="h-3.5 w-3.5" aria-hidden />,
  Abstain: <MinusCircle className="h-3.5 w-3.5" aria-hidden />,
};

const TONE: Record<VerdictLabel, "supported" | "refuted" | "unknown" | "abstain"> = {
  Supported: "supported",
  Refuted: "refuted",
  NotEnoughEvidence: "unknown",
  Abstain: "abstain",
};

const LABEL: Record<VerdictLabel, string> = {
  Supported: "Supported",
  Refuted: "Refuted",
  NotEnoughEvidence: "Not enough evidence",
  Abstain: "Abstain",
};

export function VerdictChip({ verdict, className = "" }: { verdict: VerdictLabel; className?: string }) {
  return (
    <Badge
      tone={TONE[verdict]}
      className={`px-3 py-1 text-sm font-semibold tracking-tight ${className}`}
    >
      {ICONS[verdict]}
      <span>{LABEL[verdict]}</span>
    </Badge>
  );
}

export default VerdictChip;
