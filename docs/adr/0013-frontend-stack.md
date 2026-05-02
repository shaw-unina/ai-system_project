# ADR-0013 — Frontend stack

**Status:** accepted (Phase 10).

## Context

Phase 10 needs an end-user `/verify` page and an operator dashboard.
Phase 2 named "React + Tailwind"; the user picked Next.js as the React
framework at the start of this phase. The bar is a small reviewable
surface (≤ 30 minutes of frontend review), no auth, no SSR data
fetching beyond what the API gives, no state-management library.

## Decision

| Concern | Choice | Why |
|---|---|---|
| Framework | Next.js 15 App Router | User's pick; modern default; gives us API routes for the proxy pattern (ADR-0014). |
| Language | TypeScript strict | Matches "typed end-to-end" goal; mirrors the FastAPI `VerifyResponse`. |
| Styling | Tailwind CSS | Tiny review surface; consistent with phases.md. |
| Data fetching | TanStack React Query | Mutations + polling + retry without writing a state-mgmt layer. |
| Charts | Recharts | React-native, small enough, two charts only. |
| Markdown | react-markdown + remark-gfm | Renders Phase 7 reports verbatim with table support. |
| Tests | Vitest + @testing-library/react + jsdom | Fast, no Jest config heroics. |

No Zustand, Redux, MobX, or similar — React Query plus per-component
`useState` is enough.

## Consequences

- Two test runners in the repo (pytest + Vitest). Documented in
  `frontend/README.md`; CI runs them as parallel jobs.
- Recharts adds ~70 KB gzipped to the operator route. Acceptable for
  an internal dashboard.
- The `/verify` route stays under ~110 KB First Load JS — fine for the
  user-facing surface.
