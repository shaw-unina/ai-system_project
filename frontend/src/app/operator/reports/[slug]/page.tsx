"use client";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { use } from "react";
import { fetchReport } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };

export default function ReportPage({ params }: Props) {
  const { slug } = use(params);
  const { data, isError, isLoading } = useQuery({
    queryKey: ["report", slug],
    queryFn: () => fetchReport(slug),
  });

  return (
    <div className="space-y-4">
      <a className="text-xs text-blue-700 underline" href="/operator">
        ← back to operator
      </a>
      <h1 className="text-xl font-semibold font-mono">{slug}</h1>
      {isLoading && <p className="text-sm text-slate-500">Loading…</p>}
      {isError && <p className="text-sm text-rose-700">Could not load report.</p>}
      {data && (
        <article
          className="prose prose-slate max-w-none rounded border border-slate-200 bg-white p-4 text-sm"
          data-testid="report-content"
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data}</ReactMarkdown>
        </article>
      )}
    </div>
  );
}
