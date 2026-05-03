"use client";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import VerdictCard from "@/components/VerdictCard";
import SecondOpinionCard from "@/components/SecondOpinionCard";
import { postVerify } from "@/lib/api";
import { recordIfLowConf } from "@/lib/lowconf";
import type { VerifyResponse } from "@/lib/types";

const MAX = 4000;

export default function VerifyPage() {
  const [claim, setClaim] = useState("");
  const [submittedClaim, setSubmittedClaim] = useState<string | null>(null);
  const [response, setResponse] = useState<VerifyResponse | null>(null);

  const mutation = useMutation({
    mutationFn: () => postVerify(claim),
    onSuccess: (r) => {
      recordIfLowConf(claim, r);
      setResponse(r);
      setSubmittedClaim(claim);
    },
  });

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-brand-700">
          verify
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
          Verify a claim
        </h1>
        <p className="max-w-2xl text-sm leading-relaxed text-ink-muted">
          Paste a short factual claim. The system will retrieve evidence, score
          it, and return a verdict with confidence and rationale.
        </p>
      </header>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (claim.trim().length > 0 && claim.length <= MAX) mutation.mutate();
        }}
        className="space-y-3"
      >
        <div className="rounded-2xl border border-border bg-card p-1 shadow-soft transition-colors focus-within:border-brand-500">
          <textarea
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            maxLength={MAX}
            rows={4}
            placeholder="e.g. The Eiffel Tower is in Paris."
            className="block w-full resize-y rounded-xl bg-transparent p-4 font-display text-base leading-relaxed text-ink placeholder:text-ink-muted focus:outline-none"
            data-testid="claim-input"
          />
        </div>
        <div className="flex items-center justify-between gap-3">
          <button
            type="submit"
            disabled={mutation.isPending || claim.trim().length === 0}
            className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-brand-700 px-5 py-2 text-sm font-medium text-white shadow-soft transition-colors hover:bg-brand-800 disabled:cursor-not-allowed disabled:opacity-50"
            data-testid="verify-submit"
          >
            {mutation.isPending ? (
              <>
                <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 animate-spin motion-reduce:hidden" aria-hidden>
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
                  <path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                </svg>
                Verifying…
              </>
            ) : (
              <>Verify <span aria-hidden>→</span></>
            )}
          </button>
          <span className="font-mono text-[11px] tabular-nums text-ink-muted">
            {claim.length} / {MAX}
          </span>
        </div>
      </form>

      {mutation.isError && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
          <p className="font-semibold">Verify failed</p>
          <p className="mt-0.5 font-mono text-xs">
            {(mutation.error as Error).message}
          </p>
        </div>
      )}

      {response && submittedClaim && (
        <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
          <VerdictCard response={response} />
          <SecondOpinionCard claim={submittedClaim} />
        </div>
      )}
    </div>
  );
}
