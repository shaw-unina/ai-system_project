"use client";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import VerdictCard from "@/components/VerdictCard";
import { postVerify } from "@/lib/api";
import { recordIfLowConf } from "@/lib/lowconf";
import type { VerifyResponse } from "@/lib/types";

const MAX = 4000;

export default function VerifyPage() {
  const [claim, setClaim] = useState("");
  const [response, setResponse] = useState<VerifyResponse | null>(null);

  const mutation = useMutation({
    mutationFn: () => postVerify(claim),
    onSuccess: (r) => {
      recordIfLowConf(claim, r);
      setResponse(r);
    },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Verify a claim</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (claim.trim().length > 0 && claim.length <= MAX) mutation.mutate();
        }}
        className="space-y-3"
      >
        <textarea
          value={claim}
          onChange={(e) => setClaim(e.target.value)}
          maxLength={MAX}
          rows={4}
          placeholder="Paste a claim to verify (≤ 4000 characters)…"
          className="w-full rounded border border-slate-300 p-2 text-sm font-mono"
          data-testid="claim-input"
        />
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={mutation.isPending || claim.trim().length === 0}
            className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            data-testid="verify-submit"
          >
            {mutation.isPending ? "Verifying…" : "Verify"}
          </button>
          <span className="text-xs text-slate-500">
            {claim.length} / {MAX}
          </span>
        </div>
      </form>

      {mutation.isError && (
        <p className="text-sm text-rose-700">
          Error: {(mutation.error as Error).message}
        </p>
      )}

      {response && <VerdictCard response={response} />}
    </div>
  );
}
