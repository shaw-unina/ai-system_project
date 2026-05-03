# ADR-0019 — Design system: editorial minimalism + bento operator

**Status:** accepted (Phase 11.1, UI overhaul).

## Context

The first frontend cut (Phase 10) shipped a generic Tailwind look that
felt LLM-generated. Two surfaces have very different needs: end-user
`/verify` benefits from an editorial, calm, trust-forward identity;
`/operator` benefits from data density. One-size-fits-all wasn't going
to work.

## Decision

Two style families, one design system.

- **Editorial minimalism** for `/` and `/verify` — Newsreader display
  serif, generous whitespace, brand teal accent, single-column reading
  width.
- **Bento dashboard** for `/operator` — modular `Tile` cards on a
  CSS grid, KPI tiles + sparkline + verdict-mix bar, live "pulse"
  affordance on the streaming chart.
- Shared **palette + typography + components** so the two surfaces feel
  like one product.

### Picks

| Token | Value |
|---|---|
| Display | `Newsreader` 400/500/600/700 (Google Fonts via `next/font`) |
| Body / UI | `Roboto` 300/400/500/700 |
| Brand | `#0f766e` (teal-700) |
| Accent | `#0369a1` (sky-700) |
| Background | `#fafaf7` (paper) |
| Surface | `#ffffff` |
| Verdict / Supported | `#047857` on `#ecfdf5` |
| Verdict / Refuted | `#b91c1c` on `#fef2f2` |
| Verdict / NEE | `#b45309` on `#fffbeb` |
| Verdict / Abstain | `#475569` on `#f8fafc` |
| Card radius | `1rem` |
| Shadow | `0 1px 2px rgba(2,6,23,.05), 0 4px 12px rgba(2,6,23,.04)` |

### Components

- `Badge`, `Card` / `CardHeader` — shared primitives in `components/ui/`.
- `VerdictChip` — semantic icon + label per `VerdictLabel`.
- `ConfidenceDial` — semicircle SVG meter with τ tick at the
  low-confidence threshold. Replaces the flat `ConfidenceMeter`.
- `Markdown` — `react-markdown` + `remark-gfm` wrapper with a `prose`
  theme aligned to the typography pair.
- `EvidenceList` — collapses to 3 items, "show N more" pattern, hover
  reveal for full snippet via `<details>`.
- `DisclosureBadge` — replaces the full-width banner with a popover
  pill in the nav (still discoverable, no longer noisy).
- `PoweredByGoogle` — official 4-color "G" mark + small-caps label;
  required attribution for Fact Check Tools API results.
- `Sparkline`, `Tile`, `KpiTile` — operator primitives.

### Accessibility

- All verdict colours pass 4.5:1 on their tinted backgrounds in light
  mode (verified with the palette).
- Verdict communicated by **icon + text + colour**, never colour alone.
- `ConfidenceDial` exposes `role="meter"` with `aria-valuenow/min/max`
  and an accessible name that includes a "below threshold" cue when
  applicable.
- Live tile pulse respects `prefers-reduced-motion`.
- Show-more on the evidence list is a real `<button>` with `aria-live`
  on the list.
- Disclosure popover: keyboard-openable, traps focus, `Esc` to close.

## Alternatives considered

| Option | Why not |
|---|---|
| Glassmorphism / brutalism | Wrong product identity for a fact-checker. |
| Single style across both surfaces | Either operator gets too sparse or `/verify` gets too dense. |
| Banner kept on every page | Violated "the safety message should be visible without being noisy." |
| `shadcn/ui` adopt | Worth doing post-1.0; for now we stay on hand-built primitives to keep the dep footprint flat. |

## Consequences

- Adds `@tailwindcss/typography` dev dep for the markdown `prose`
  theme. `next/font/google` handles font delivery — no extra runtime
  request, no FOUT.
- The DisclosureBanner / ConfidenceMeter components are deleted.
  Tests updated to target `DisclosureBadge` + `ConfidenceDial`.
- `/verify` First Load JS rises slightly (markdown + dial) but stays
  well under the previous 110 kB envelope.
