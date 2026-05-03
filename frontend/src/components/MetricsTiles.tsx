"use client";
import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchMetricsText } from "@/lib/api";
import { parsePromText, summarise } from "@/lib/metrics";
import { KpiTile, Tile } from "./operator/Tile";
import Sparkline from "./Sparkline";
import VerdictMixChart from "./VerdictMixChart";

const MAX_SAMPLES = 30;

export default function MetricsTiles() {
  const { data, isError, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ["metrics"],
    queryFn: fetchMetricsText,
    refetchInterval: 10_000,
    refetchIntervalInBackground: false,
  });

  const [latencyHistory, setLatencyHistory] = useState<number[]>([]);
  const lastSeenAt = useRef(0);

  useEffect(() => {
    if (!data || dataUpdatedAt === lastSeenAt.current) return;
    lastSeenAt.current = dataUpdatedAt;
    const sum = summarise(parsePromText(data));
    if (sum.latencyP95 != null) {
      setLatencyHistory((prev) => [...prev.slice(-MAX_SAMPLES + 1), sum.latencyP95!]);
    }
  }, [data, dataUpdatedAt]);

  if (isLoading) {
    return (
      <div data-testid="metrics-tiles" className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <Tile key={i} title="loading">
            <div className="h-7 w-20 animate-pulse rounded bg-muted" />
          </Tile>
        ))}
      </div>
    );
  }
  if (isError || !data) {
    return (
      <Tile title="Service health" testId="metrics-tiles">
        <p className="text-sm text-red-500 dark:text-red-400">Service metrics are unavailable right now.</p>
      </Tile>
    );
  }

  const summary = summarise(parsePromText(data));
  const totalRequests = Object.values(summary.requestsTotal).reduce((a, b) => a + b, 0);
  const meanLatencyMs =
    summary.latencyCount > 0 ? (summary.latencySum / summary.latencyCount) * 1000 : 0;

  return (
    <div data-testid="metrics-tiles" className="space-y-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <KpiTile title="Requests" value={totalRequests} />
        <KpiTile
          title="Median latency"
          value={summary.latencyP50 != null ? summary.latencyP50.toFixed(2) : "—"}
          unit={summary.latencyP50 != null ? "s" : ""}
        />
        <KpiTile
          title="Slowest 5%"
          value={summary.latencyP95 != null ? summary.latencyP95.toFixed(2) : "—"}
          unit={summary.latencyP95 != null ? "s" : ""}
        />
        <KpiTile title="Average" value={meanLatencyMs.toFixed(0)} unit="ms" />
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <Tile
          title="Recent latency"
          right={
            <span className="inline-flex items-center gap-1.5">
              <span className="relative inline-flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-500 opacity-60 motion-reduce:animate-none" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand-700" />
              </span>
              live
            </span>
          }
          className="lg:col-span-2"
        >
          <Sparkline values={latencyHistory} width={520} height={64} className="w-full" />
        </Tile>
        <Tile title="Verdict mix">
          <VerdictMixChart counts={summary.verdictsTotal} />
        </Tile>
      </div>
    </div>
  );
}
