# Phase 11 — Decisions

| # | Decision | Rationale |
|---|---|---|
| ADR-0015 | Bearer-token auth + per-key sliding-window rate limit, no users | Smallest surface that gates abuse without adopting a user model. |
| ADR-0016 | `/operator` cookie gate via single `OPERATOR_PASSWORD`; `/verify` stays open | The demo surface needs to stay frictionless; operator surface needs *some* gate before public deploy. |

## Notable trade-offs

- **No SSO / user accounts.** Dashboard auth is one shared password; API
  auth is a static key list. Real identity is post-1.0.
- **Self-rolled rate limiter** in `services/auth.py` (~30 lines, in-process,
  threadsafe). Avoided `slowapi` to keep the dep surface tight; a
  multi-instance deployment would need to swap this for a Redis-backed
  bucket.
- **Hand-written prompt-safety**: NFKC + control/zero-width strip + fence
  neutralisation + delimited-block wrap. Did not adopt a third-party
  jailbreak detector — too high a false-positive surface for a fact-checker
  whose user content frequently *quotes* the very text adversaries craft.
- **Cosign keyless** signing rather than a managed KMS key. The release
  workflow tolerates failure (`continue-on-error`) so first-time runs can
  surface the OIDC config gap without breaking the publish.
- **Perf reports are not generated in CI.** Runner variance makes the
  numbers misleading; the Makefile targets are documented as a release
  step.

## Risks tracked into post-1.0

- Sliding-window rate limit is per-process: a multi-replica deploy
  multiplies the effective quota by replica count.
- Dashboard cookie is a long-lived bearer-equivalent (8h). Rotation is
  manual.
- Prompt-safety regex won't catch base64-encoded or homoglyph attacks.
- `pip-audit` / `npm audit` / `gitleaks` are advisory in CI — flip to
  blocking once the allowlists are curated.
- OpenAPI drift check runs only when the committed types file exists; the
  Phase 10 hand-written `src/lib/types.ts` mirror is still load-bearing.
