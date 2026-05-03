"use client";
import { useEffect, useRef, useState } from "react";

export function DisclosureBadge() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onEsc);
    };
  }, [open]);

  return (
    <div ref={ref} className="relative" data-testid="disclosure-badge">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-haspopup="dialog"
        className="group inline-flex cursor-pointer items-center gap-1.5 rounded-full bg-verdict-unknown-bg px-2.5 py-1 text-xs font-medium text-verdict-unknown ring-1 ring-inset ring-verdict-unknown-ring transition-colors hover:opacity-90"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" className="h-3.5 w-3.5" aria-hidden>
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h.01a1 1 0 100-2H10v-3a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        AI-generated
      </button>
      {open && (
        <div
          role="dialog"
          aria-label="AI disclosure"
          className="absolute right-0 top-full z-40 mt-2 w-72 rounded-xl border border-border bg-card p-4 text-sm text-ink shadow-soft"
        >
          <div className="font-display text-base font-semibold">AI-generated output</div>
          <p className="mt-2 leading-relaxed text-ink-muted">
            Verdicts, confidence scores, evidence summaries, and rationales are
            produced by a language model over retrieved evidence. Always
            review the sources before citing or acting on a verdict.
          </p>
        </div>
      )}
    </div>
  );
}

export default DisclosureBadge;
