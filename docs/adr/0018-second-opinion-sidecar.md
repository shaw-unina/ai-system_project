# ADR-0018 — Second-opinion sidecar (Google Fact Check Tools)

**Status:** accepted (Phase 11.1).

## Context

Showing the user how *other* fact-checkers rated the same claim is a
clean transparency win (NFR-Trans-2). Wiring it as **evidence** would
corrupt our calibration — the LLM would just rephrase PolitiFact and the
confidence numbers would inherit a different system's quality. Wiring it
as **display** preserves both signals as independent.

## Decision

- New endpoint `GET /v1/second-opinion?claim=…` in
  [src/misinfo/services/second_opinion.py](../../src/misinfo/services/second_opinion.py).
- Backed by Google Fact Check Tools v1alpha1 `claims:search`.
- Always returns 200; the `source` field encodes
  `disabled` / `unavailable` / `google_fact_check_tools_v1alpha1` so the
  frontend renders states cleanly.
- 24h in-process LRU cache keyed by `sha256(claim)` to bound API cost.
- Same auth + rate-limit dependencies as `/v1/verify`.
- Frontend [SecondOpinionCard.tsx](../../frontend/src/components/SecondOpinionCard.tsx)
  fetches independently of the verify mutation so a slow / failing FC
  API doesn't block the verdict.

## Alternatives considered

| Option | Why not |
|---|---|
| Use FC results as evidence | Conflates two different systems' verdicts; breaks calibration. |
| Skip the sidecar entirely | Misses a real transparency win for ~1 day of work. |
| Build our own fact-check aggregator | Out of scope; that's a different product. |

## Consequences

- Claim text now flows to a third (Google) party when the sidecar is
  enabled. Documented in `LIMITATIONS.md`.
- The sidecar's latency is **not** part of NFR-Lat-1 — it's a separate
  request rendered in parallel.
- The 24h cache is in-process; multi-replica deploys multiply Google
  quota usage by replica count.
- Disabled by default (no key set) — the dashboard renders a one-line
  "disabled" state and the verdict still ships.
