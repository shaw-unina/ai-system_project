"use client";
import { useQuery } from "@tanstack/react-query";
import { fetchReportList } from "@/lib/api";

export default function ReportList() {
  const { data, isError, isLoading } = useQuery({
    queryKey: ["report-list"],
    queryFn: fetchReportList,
  });

  if (isLoading) return <p className="text-sm text-slate-500">Loading reports…</p>;
  if (isError) return <p className="text-sm text-rose-700">Could not load reports.</p>;
  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-slate-500 italic">
        No reports under <code>reports/_smoke/</code>. Run{" "}
        <code>misinfo phase7 --smoke</code> to generate them.
      </p>
    );
  }

  return (
    <ul className="space-y-1" data-testid="report-list">
      {data.map((slug) => (
        <li key={slug}>
          <a
            className="text-sm text-blue-700 hover:underline"
            href={`/operator/reports/${encodeURIComponent(slug)}`}
          >
            {slug}
          </a>
        </li>
      ))}
    </ul>
  );
}
