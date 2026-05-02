# Dataset card — FakeNewsNet (PolitiFact, text-only)

**Status:** DRAFT
**Registry key:** `fakenewsnet@politifact-text`
**License:** MIT (code); publisher/Twitter terms (data)
**Homepage:** https://github.com/KaiDMML/FakeNewsNet

## Motivation

FakeNewsNet was originally proposed (Shu et al. 2020) as a multi-source news dataset combining article content, social context (tweets), and meta-data. Since the Twitter API closure (2023), tweet rehydration is no longer practical for new users. We retain only the **PolitiFact text portion** (titles + URLs + binary fake/real label) as a cheap **drift / cross-domain slice** — not as a primary benchmark.

## Composition

- Two CSVs as shipped by the upstream repo: `politifact_fake.csv`, `politifact_real.csv`.
- Per-row fields used: `id`, `news_url`, `title`. We discard tweet-id and social-graph columns.

## Collection process

PolitiFact is a US fact-checking organisation; FakeNewsNet pairs each verified item with the article URL the fact-check addressed.

## Preprocessing we apply

- NFC unicode normalisation + whitespace collapse + ≤4 000 character clip on `title`, used as the `claim` text.
- Label flattened to `{fake, real}`; original PolitiFact 6-class verdicts are not preserved.

## Splits

- We treat the union as a single evaluation slice. Random splits are not used; if a stratified split is needed, we time-order by article publication date (where available).

## Intended uses

- Cross-domain slice in Phase 7 to test whether the AVeriTeC-tuned system survives off-distribution.
- Sanity baseline only — not headline-reportable.

## Out-of-scope uses

- Production deployment.
- Truth labelling for the underlying news articles.
- Any analysis that requires the social-context features (we don't load them).

## Known biases / limitations

- **US-political skew.** PolitiFact is a US-centric fact-checker.
- **Topic narrowness.** The slice does not cover health, climate, or non-political domains.
- **Label noise.** Six-class PolitiFact verdicts collapsed to binary loses nuance (e.g. "half-true" → ?).
- **Missing tweets.** Anything depending on social-context features is unavailable.
- **Data rot.** Source URLs may be dead.

## Distribution

- Users clone the upstream repo and place the two CSVs under `data/raw/fakenewsnet/politifact-text/`.
- We do not redistribute the CSVs.

## Maintenance

- File hashes committed to `data/manifest.json`.
- Card updated when upstream restructures or when we expand to other FakeNewsNet sources.
