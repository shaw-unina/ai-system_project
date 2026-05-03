"use client";
import { useQuery } from "@tanstack/react-query";
import { use } from "react";
import { fetchReport } from "@/lib/api";
import Card from "@/components/ui/Card";
import Markdown from "@/components/Markdown";

type Props = { params: Promise<{ slug: string }> };

export default function ReportPage({ params }: Props) {
  const { slug } = use(params);
  const { data, isError, isLoading } = useQuery({
    queryKey: ["report", slug],
    queryFn: () => fetchReport(slug),
  });

  return (
    <div className="space-y-6">
      <a
        className="inline-flex items-center gap-1 text-xs text-ink-muted hover:text-ink"
        href="/operator"
      >
        <span aria-hidden>←</span> back to operator
      </a>
      <header className="space-y-1">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-brand-700">
          report
        </p>
        <h1 className="font-mono text-lg text-ink">{slug}</h1>
      </header>
      {isLoading && <p className="text-sm text-ink-muted">Loading…</p>}
      {isError && (
        <p className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">
          Could not load report.
        </p>
      )}
      {data && (
        <Card className="p-6" data-testid="report-content">
          <Markdown>{data}</Markdown>
        </Card>
      )}
    </div>
  );
}
