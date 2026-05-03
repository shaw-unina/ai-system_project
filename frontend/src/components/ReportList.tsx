"use client";
import { useQuery } from "@tanstack/react-query";
import { fetchReportList } from "@/lib/api";

export default function ReportList() {
  const { data, isError, isLoading } = useQuery({
    queryKey: ["report-list"],
    queryFn: fetchReportList,
  });

  if (isLoading) {
    return (
      <ul className="space-y-1.5" data-testid="report-list-loading">
        {[0, 1, 2].map((i) => (
          <li key={i} className="h-4 animate-pulse rounded bg-muted" />
        ))}
      </ul>
    );
  }
  if (isError) return <p className="text-sm text-red-500 dark:text-red-400">Could not load reports.</p>;
  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-ink-muted">No evaluation reports available yet.</p>
    );
  }

  return (
    <ul className="divide-y divide-border" data-testid="report-list">
      {data.map((slug) => (
        <li key={slug}>
          <a
            className="group flex items-center justify-between gap-3 py-2 text-sm text-ink transition-colors hover:text-accent-700"
            href={`/operator/reports/${encodeURIComponent(slug)}`}
          >
            <span className="truncate font-mono text-xs">{slug}</span>
            <span className="text-ink-muted opacity-0 transition-opacity group-hover:opacity-100">
              open ↗
            </span>
          </a>
        </li>
      ))}
    </ul>
  );
}
