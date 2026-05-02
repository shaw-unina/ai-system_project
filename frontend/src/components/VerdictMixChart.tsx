"use client";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Props {
  counts: Record<string, number>;
}

export default function VerdictMixChart({ counts }: Props) {
  const data = Object.entries(counts).map(([verdict, n]) => ({ verdict, n }));
  if (data.length === 0) {
    return (
      <p className="text-sm text-slate-500 italic">
        No verdicts recorded yet. Submit a claim on{" "}
        <a className="underline" href="/verify">
          /verify
        </a>
        .
      </p>
    );
  }
  return (
    <div className="rounded border border-slate-200 bg-white p-3" data-testid="verdict-mix-chart">
      <p className="text-xs uppercase text-slate-500 mb-1">Verdict mix</p>
      <div style={{ width: "100%", height: 200 }}>
        <ResponsiveContainer>
          <BarChart data={data}>
            <XAxis dataKey="verdict" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="n" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
