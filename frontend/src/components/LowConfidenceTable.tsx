"use client";
import { useEffect, useState } from "react";
import { clearLowConf, loadLowConf } from "@/lib/lowconf";
import type { LowConfRow, VerdictLabel } from "@/lib/types";
import VerdictChip from "./VerdictChip";

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
      <p className="text-sm text-ink-muted" data-testid="lowconf-empty">
        No low-confidence verdicts in this session yet.
      </p>
    );
  }

  return (
    <div data-testid="lowconf-table">
      <ul className="divide-y divide-ink/5">
        {rows.map((r) => (
          <li key={r.request_id} className="grid grid-cols-[80px_1fr_70px] items-center gap-3 py-2 text-sm">
            <span className="font-mono text-[11px] text-ink-muted">
              {new Date(r.ts).toLocaleTimeString()}
            </span>
            <div className="flex min-w-0 items-center gap-2">
              <VerdictChip verdict={r.verdict as VerdictLabel} />
              <span className="truncate text-ink/80" title={r.claim_preview}>
                {r.claim_preview}
              </span>
            </div>
            <span className="text-right font-mono text-xs tabular-nums text-ink-muted">
              {r.confidence.toFixed(3)}
            </span>
          </li>
        ))}
      </ul>
      <button
        type="button"
        className="mt-3 cursor-pointer text-xs text-ink-muted hover:text-ink hover:underline"
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
