import type { VerifyResponse } from "@/lib/types";

export const mkVerify = (overrides: Partial<VerifyResponse> = {}): VerifyResponse => ({
  verdict: "Supported",
  confidence: 0.85,
  evidence: [
    { source_id: "wiki:paris", url: null, span: "paris is the capital of france", score: 0.9 },
  ],
  rationale: "evidence supports the claim",
  metadata: {
    backend: "mock",
    model_id: "mock",
    model_version: "0",
    seed: 42,
    temperature: 0.0,
    config_hash: "abc",
    dataset_hash: null,
    langfuse_trace_id: null,
    generated_at_utc: "2026-05-02T00:00:00+00:00",
  },
  disclosure: "ai_generated",
  low_confidence: false,
  request_id: "req-fixture",
  latency_ms: 123.4,
  ...overrides,
});
