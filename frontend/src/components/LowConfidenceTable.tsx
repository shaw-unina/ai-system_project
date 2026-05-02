"use client";
import { useEffect, useState } from "react";
import { clearLowConf, loadLowConf } from "@/lib/lowconf";
import type { LowConfRow } from "@/lib/types";

export default function LowConfidenceTable() {
  const [rows, setRows] = useState<LowConfRow[]>([]);

  useEffect(() => {
    setRows(loadLowConf());
    const onStorage = () => setRows(loadLowConf());
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  if (rows.length === 0) {
    return (
      <p className="text-sm text-slate-500 italic" data-testid="lowconf-empty">
        No low-confidence verdicts in this session yet.
      </p>
    );
  }

  return (
    <div data-testid="lowconf-table">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b">
            <th className="py-1 pr-3">When</th>
            <th className="py-1 pr-3">Verdict</th>
            <th className="py-1 pr-3">Conf.</th>
            <th className="py-1">Claim</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.request_id} className="border-b last:border-0">
              <td className="py-1 pr-3 font-mono text-xs text-slate-500">
                {new Date(r.ts).toLocaleTimeString()}
              </td>
              <td className="py-1 pr-3">{r.verdict}</td>
              <td className="py-1 pr-3 tabular-nums">{r.confidence.toFixed(3)}</td>
              <td className="py-1 truncate">{r.claim_preview}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button
        type="button"
        className="mt-3 text-xs text-slate-500 underline"
        onClick={() => {
          clearLowConf();
          setRows([]);
        }}
        data-testid="lowconf-clear"
      >
        Clear session list
      </button>
    </div>
  );
}
