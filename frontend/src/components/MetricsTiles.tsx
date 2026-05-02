"use client";
import { useQuery } from "@tanstack/react-query";
import { fetchMetricsText } from "@/lib/api";
import { parsePromText, summarise } from "@/lib/metrics";
import VerdictMixChart from "./VerdictMixChart";

export default function MetricsTiles() {
  const { data, isError, isLoading } = useQuery({
    queryKey: ["metrics"],
    queryFn: fetchMetricsText,
    refetchInterval: 10_000,
    refetchIntervalInBackground: false,
  });

  if (isLoading) return <p className="text-sm text-slate-500">Loading metrics…</p>;
  if (isError || !data) {
    return (
      <p className="text-sm text-rose-700">
        Could not reach <code>/metrics</code>. Is the backend running?
      </p>
    );
  }

  const summary = summarise(parsePromText(data));
  const totalRequests = Object.values(summary.requestsTotal).reduce((a, b) => a + b, 0);
  const meanLatencyMs =
    summary.latencyCount > 0 ? (summary.latencySum / summary.latencyCount) * 1000 : 0;

  return (
    <div data-testid="metrics-tiles" className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Tile label="Requests (total)" value={totalRequests.toString()} />
        <Tile
          label="Latency p50"
          value={summary.latencyP50 != null ? `${summary.latencyP50.toFixed(2)} s` : "—"}
        />
        <Tile
          label="Latency p95"
          value={summary.latencyP95 != null ? `${summary.latencyP95.toFixed(2)} s` : "—"}
        />
        <Tile label="Latency mean" value={`${meanLatencyMs.toFixed(0)} ms`} />
      </div>
      <VerdictMixChart counts={summary.verdictsTotal} />
    </div>
  );
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-slate-200 bg-white p-3">
      <p className="text-xs uppercase text-slate-500">{label}</p>
      <p className="text-2xl font-semibold tabular-nums">{value}</p>
    </div>
  );
}
