"use client";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const COLORS: Record<string, string> = {
  Supported: "#047857",
  Refuted: "#b91c1c",
  NotEnoughEvidence: "#b45309",
  Abstain: "#475569",
};

const SHORT: Record<string, string> = {
  Supported: "Sup",
  Refuted: "Ref",
  NotEnoughEvidence: "NEE",
  Abstain: "Abs",
};

export default function VerdictMixChart({ counts }: { counts: Record<string, number> }) {
  const data = Object.entries(counts).map(([verdict, n]) => ({
    verdict,
    short: SHORT[verdict] ?? verdict.slice(0, 3),
    n,
  }));
  if (data.length === 0) {
    return (
      <p className="text-sm text-ink-muted">
        No verdicts yet. Submit a claim on{" "}
        <a className="text-accent-700 hover:underline" href="/verify">
          /verify
        </a>
        .
      </p>
    );
  }
  return (
    <div data-testid="verdict-mix-chart" className="-mx-2">
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
          <XAxis
            dataKey="short"
            tick={{ fill: "#475569", fontSize: 11 }}
            axisLine={{ stroke: "#e5e7eb" }}
            tickLine={false}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fill: "#475569", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(15,118,110,.06)" }}
            contentStyle={{
              borderRadius: 8,
              border: "1px solid #e5e7eb",
              fontSize: 12,
              padding: "6px 8px",
            }}
            labelFormatter={(s, items) => items?.[0]?.payload?.verdict ?? s}
          />
          <Bar dataKey="n" radius={[6, 6, 0, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={COLORS[d.verdict] ?? "#0f766e"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
