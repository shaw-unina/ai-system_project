interface Props {
  value: number; // 0..1
}

export default function ConfidenceMeter({ value }: Props) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <div className="w-full" data-testid="confidence-meter">
      <div
        className="h-2 w-full rounded bg-slate-200 overflow-hidden"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(pct)}
      >
        <div
          className="h-full bg-emerald-500"
          style={{ width: `${pct}%` }}
          data-testid="confidence-bar"
        />
      </div>
      <span className="text-xs text-slate-500 tabular-nums">
        confidence {value.toFixed(3)}
      </span>
    </div>
  );
}
