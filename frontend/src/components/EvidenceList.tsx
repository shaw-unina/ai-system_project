"use client";
import { useState } from "react";
import type { EvidenceRef } from "@/lib/types";

const INITIAL = 3;
const SHORT_THRESHOLD = 240;

function host(url: string | null | undefined): string | null {
  if (!url) return null;
  try {
    return new URL(url).host.replace(/^www\./, "");
  } catch {
    return null;
  }
}

function EvidenceItem({ ref_, index }: { ref_: EvidenceRef; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const h = host(ref_.url);
  const score = Math.max(0, Math.min(1, ref_.score || 0));
  const text = ref_.span ?? "";
  const isLong = text.length > SHORT_THRESHOLD;

  return (
    <li className="rounded-xl border border-border bg-card p-4 transition-colors hover:border-brand-100 hover:bg-brand-50/30">
      <div className="mb-1.5 flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-wider text-ink-muted">
            #{index + 1}
          </span>
          {h && <span className="truncate text-xs font-medium text-ink">{h}</span>}
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium tabular-nums text-muted-foreground">
            {score.toFixed(2)}
          </span>
          {ref_.url && (
            <a
              href={ref_.url}
              target="_blank"
              rel="noreferrer noopener"
              className="text-[11px] font-medium text-accent-700 hover:underline"
            >
              source ↗
            </a>
          )}
        </div>
      </div>
      <p
        className={`whitespace-pre-wrap text-sm leading-relaxed text-foreground/80 ${
          isLong && !expanded ? "line-clamp-3" : ""
        }`}
      >
        {text}
      </p>
      {isLong && (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="mt-1 cursor-pointer text-[11px] font-medium text-ink-muted hover:text-ink"
          aria-expanded={expanded}
        >
          {expanded ? "show less" : "show more"}
        </button>
      )}
    </li>
  );
}

export default function EvidenceList({ evidence }: { evidence: EvidenceRef[] }) {
  const [showAll, setShowAll] = useState(false);
  if (!evidence.length) {
    return (
      <p className="text-sm text-ink-muted" data-testid="evidence-empty">
        No evidence retrieved.
      </p>
    );
  }
  const visible = showAll ? evidence : evidence.slice(0, INITIAL);
  const remaining = evidence.length - INITIAL;
  return (
    <div className="space-y-3" data-testid="evidence-list">
      <div className="flex items-baseline justify-between">
        <h3 className="font-display text-sm font-semibold text-ink">
          Evidence <span className="text-ink-muted">({evidence.length})</span>
        </h3>
        {!showAll && remaining > 0 && (
          <button
            type="button"
            onClick={() => setShowAll(true)}
            className="cursor-pointer text-xs font-medium text-accent-700 hover:underline"
            data-testid="evidence-show-more"
          >
            show {remaining} more
          </button>
        )}
        {showAll && evidence.length > INITIAL && (
          <button
            type="button"
            onClick={() => setShowAll(false)}
            className="cursor-pointer text-xs font-medium text-ink-muted hover:text-ink"
          >
            collapse
          </button>
        )}
      </div>
      <ul className="space-y-2.5" aria-live="polite">
        {visible.map((e, i) => (
          <EvidenceItem key={`${e.source_id}-${i}`} ref_={e} index={i} />
        ))}
      </ul>
    </div>
  );
}
