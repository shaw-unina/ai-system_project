"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchSecondOpinion } from "@/lib/api";
import type { SecondOpinionEntry, SecondOpinionResponse } from "@/lib/types";
import Card, { CardHeader } from "./ui/Card";
import Badge from "./ui/Badge";
import PoweredByGoogle from "./PoweredByGoogle";

function ratingTone(rating: string): "supported" | "refuted" | "unknown" | "abstain" | "neutral" {
  const r = rating.toLowerCase().trim();
  if (!r) return "neutral";
  if (/(true|correct|accurate|supported|confirmed)/.test(r) && !/false|not/.test(r)) return "supported";
  if (/(false|incorrect|fake|fabricated|debunk)/.test(r)) return "refuted";
  if (/(mixture|mixed|partly|misleading|missing context|unproven|exaggerated)/.test(r)) return "unknown";
  return "abstain";
}

function host(url: string): string {
  try {
    return new URL(url).host.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function fmtDate(d?: string | null): string | null {
  if (!d) return null;
  const dt = new Date(d);
  if (Number.isNaN(dt.getTime())) return d.slice(0, 10);
  return dt.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function Entry({ entry }: { entry: SecondOpinionEntry }) {
  const tone = ratingTone(entry.rating);
  const date = fmtDate(entry.review_date);
  return (
    <li className="rounded-xl border border-border bg-card p-3 transition-colors hover:border-brand-100">
      <div className="flex items-start justify-between gap-2">
        <a
          href={entry.review_url}
          target="_blank"
          rel="noreferrer noopener"
          className="text-sm font-semibold text-ink hover:text-accent-700"
        >
          {entry.publisher}
          <span className="ml-1 text-[10px] font-normal text-ink-muted">
            ↗ {host(entry.review_url)}
          </span>
        </a>
      </div>
      <div className="mt-1 flex flex-wrap items-center gap-2">
        <Badge tone={tone}>{entry.rating || "unrated"}</Badge>
        {date && <span className="text-[11px] text-ink-muted">{date}</span>}
      </div>
      {entry.claim_text && entry.claim_text !== entry.publisher && (
        <p className="mt-1.5 line-clamp-2 text-xs italic leading-relaxed text-foreground/70">
          “{entry.claim_text}”
        </p>
      )}
    </li>
  );
}

function Skeleton() {
  return (
    <ul className="space-y-2" data-testid="second-opinion-loading">
      {[0, 1, 2].map((i) => (
        <li key={i} className="rounded-xl border border-border bg-card p-3">
          <div className="h-3 w-1/3 animate-pulse rounded bg-muted" />
          <div className="mt-2 h-3 w-1/4 animate-pulse rounded bg-muted" />
          <div className="mt-2 h-3 w-3/4 animate-pulse rounded bg-muted" />
        </li>
      ))}
    </ul>
  );
}

export function SecondOpinionCard({ claim }: { claim: string }) {
  const { data, isLoading, isError } = useQuery<SecondOpinionResponse>({
    queryKey: ["second-opinion", claim],
    queryFn: () => fetchSecondOpinion(claim),
    enabled: claim.trim().length > 0,
    staleTime: 5 * 60 * 1000,
    retry: 0,
  });

  return (
    <Card className="overflow-hidden" data-testid="second-opinion-card">
      <CardHeader
        title="Other fact-checkers say"
        right={<span className="rounded-full bg-muted px-2 py-0.5 text-[10px] uppercase tracking-wider text-ink-muted">for context</span>}
      />
      <div className="space-y-3 p-4">
        <PoweredByGoogle />

        {isLoading && <Skeleton />}

        {isError && (
          <p data-testid="second-opinion-error" className="text-sm text-ink-muted">
            External fact-check service unavailable.
          </p>
        )}

        {data && data.source === "disabled" && (
          <p data-testid="second-opinion-disabled" className="text-sm text-ink-muted">
            Third-party fact-check lookups are not configured.
          </p>
        )}

        {data && data.source === "unavailable" && (
          <p data-testid="second-opinion-unavailable" className="text-sm text-ink-muted">
            Third-party fact-check service is unavailable right now.
          </p>
        )}

        {data &&
          data.source === "google_fact_check_tools_v1alpha1" &&
          data.results.length === 0 && (
            <p data-testid="second-opinion-empty" className="text-sm text-ink-muted">
              No published fact-checks match this claim yet.
            </p>
          )}

        {data && data.results.length > 0 && data.matched_query && data.matched_query.trim() !== claim.trim() && (
          <p className="text-[11px] text-ink-muted">
            Matched on: <span className="italic">“{data.matched_query}”</span>
          </p>
        )}

        {data && data.results.length > 0 && (
          <ul className="space-y-2" data-testid="second-opinion-list">
            {data.results.map((r, i) => (
              <Entry key={i} entry={r} />
            ))}
          </ul>
        )}

        <p className="border-t border-border pt-3 text-[11px] leading-relaxed text-ink-muted">
          Third-party verdicts shown for context. They do not feed into our
          pipeline — confidence and rationale come from our own retrieval.
        </p>
      </div>
    </Card>
  );
}

export default SecondOpinionCard;
