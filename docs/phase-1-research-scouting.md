# Phase 1 — Research Scouting

> **Goal of this phase.** Pick **one** research angle to pursue, defensibly, in ≤ 2 weeks. Output is a short *decision document* — not a thesis. Build comes later.

This document contains both the **landscape briefing** (what we found in the literature, May 2026) and the **plan** (concrete steps, deliverables, exit criteria). Phase 1 should not become a stalling tactic; the cap is hard.

---

## Part A — Landscape briefing

State of the field, distilled from a directed survey of 2023–2026 work. Citations are intentionally light — the bibliography lives at the end and gets expanded during the phase.

### A.1 Anchor surveys to read first

These four are the fastest way to reach context:

1. **Chen & Shu (2024), *"Combating Misinformation in the Age of LLMs: Opportunities and Challenges"*, AI Magazine.** The canonical "LLMs both create and detect misinformation" framing. Companion paper list at [llm-misinformation-survey](https://github.com/llm-misinformation/llm-misinformation-survey).
2. **Quelle & Bovet (2024), *"The perils and promises of fact-checking with large language models"*, Frontiers in AI.** Empirical: when LLM fact-checking helps users, when it actively hurts them.
3. **Eldifrawi et al. (2024), *"Generative LLMs in Automated Fact-Checking: A Survey"* ([arXiv:2407.02351](https://arxiv.org/abs/2407.02351)).** Pipeline-by-pipeline view: claim detection → retrieval → verification → rationale.
4. **"Hallucination to Truth: A Review of Fact-Checking and Factuality Evaluation in LLMs"* (Springer AI Review 2025, [arXiv:2508.03860](https://arxiv.org/abs/2508.03860)).** Sets up the connection between fact-checking and hallucination evaluation — directly relevant if we pick a faithfulness angle.

Plus the curated paper list at [ICTMCG/LLM-for-misinformation-research](https://github.com/ICTMCG/LLM-for-misinformation-research) for tracking what's appeared since.

### A.2 Benchmarks and shared tasks (current)

| Benchmark | Year | Domain | Why it matters |
|---|---|---|---|
| **FEVER / FEVEROUS** | 2018 / 2021 | Wikipedia-grounded claims | Still the default sanity-check benchmark. Saturated for SOTA but useful as a unit test. |
| **AVeriTeC** | 2024 → **AVeriTeC-2 (FEVER 2025 workshop)** | Real-world claims, web evidence | The current "serious" benchmark. 2025 shared task constrained systems to **open-weights, single 23 GB GPU, ≤ 1 min/claim**. Winner CTU AIC scored ~0.50 AVeriTeC score; HerO 2 second with shortest runtime. |
| **CLEF-2025 CheckThat!** | 2025 | Subjectivity, claim normalization, **numerical claims**, scientific discourse | Task 3 (numerical claims) is the freshest area; top systems sit around F1 0.55–0.60 — far from solved. |
| **LIAR / LIAR-PLUS / LIAR-RAW** | 2017–2023 | Political short statements | Cheap, noisy, good for ablations only. |
| **FakeNewsNet, ISOT** | 2018–2020 | News articles, social context | Largely "solved" on i.i.d. splits — useful for stress-testing under drift, not for headline numbers. |
| **MuMiN** | 2022 | Multilingual + multimodal social graph | Still the best public multilingual+multimodal corpus. 41 languages, ~12.9k claims. |
| **Factify 2** | 2023 | Multimodal (image+text) | Active but Twitter-API-dependent. |
| **MMM-Fact** ([arXiv:2510.25120](https://arxiv.org/abs/2510.25120)) | 2025 | Multimodal, multi-domain, with **multi-level retrieval difficulty** | Newer, designed precisely to probe retrieval failure. |
| **ClimateCheck** (SDP 2025) | 2025 | Climate-science claims with paper evidence | Niche but cleanly scoped, good for a focused study. |
| **OpenFactCheck** ([arXiv:2405.05583](https://arxiv.org/abs/2405.05583)) | 2024 | Customizable fact-checker + LLM factuality eval | Useful as an evaluation harness, not a dataset. |

Headline read: **AVeriTeC-2 is where the action is.** A new submission there is publishable; saturating LIAR isn't.

### A.3 What architectures actually win in 2026

- **Fine-tuned encoders (DeBERTa-v3, RoBERTa-large)** — still the strongest cheap baseline on i.i.d. splits and remain the de-facto NLI head inside larger pipelines. *Not* SOTA on AVeriTeC anymore.
- **RAG + LLM verifier** — current dominant pattern: claim decomposition → BM25 + dense retrieval → LLM judge with structured output. Top AVeriTeC-2 systems (CTU AIC, HerO 2) follow exactly this shape with **open-weight LLMs ≤ 8 B**.
- **Agentic fact-checkers** — ReAct-style loops with tool use (web search, calculator, KG lookup). SAFE, FIRE, and the OpenFactCheck-style decomposition pipelines fall here. Better recall on long-form / multi-hop claims, but expensive and harder to evaluate reproducibly.
- **End-to-end LLM zero/few-shot** — works as a baseline, but Quelle & Bovet's PNAS-style finding stands: confident wrong answers actively *hurt* users. Don't ship this naked.
- **Multimodal pipelines** — most are still "encode each modality + late fusion" with a verifier on top; agentic variants (e.g., [arXiv:2512.22933](https://arxiv.org/abs/2512.22933)) are emerging in late 2025.

Stack worth noting in the wild: open-weight verifiers (Llama-3.x-8B, Qwen2.5-7B, Mistral-Small), retrieval via BM25 + BGE/E5 dense, optional ColBERTv2 for high recall, web-search APIs (Tavily, Serper, Brave) when an offline corpus is insufficient.

### A.4 The seven open angles, ranked for our context

Each rated on three axes: **Open?** (is real research left to do), **Tractable in 8 weeks** (can a small team move the needle), **Course-fit** (does it land both INN and RES halves cleanly).

1. **Robustness to LLM-generated misinformation.** Detectors trained on human-written fakes degrade on machine-written ones; SheepDog and the Nature Communications 2025 detection-limits paper formalize this. Pairs naturally with the PDF's "fakes generator" companion. **Open: yes. Tractable: yes. Course-fit: very high.**
2. **Evidence retrieval failure & insufficient-evidence abstention.** Faithfulness-aware uncertainty quantification ([arXiv:2505.21072](https://arxiv.org/abs/2505.21072)) and MMM-Fact's retrieval-difficulty stratification show retrieval is the dominant failure mode in RAG fact-checkers. **Open: yes. Tractable: yes. Course-fit: high.**
3. **Faithful rationales (right verdict, wrong reasoning).** Drift (ACL 2025), HalluTree, INTRA. Hard to evaluate without human studies; metrics are still being argued about. **Open: very. Tractable: medium — eval is the bottleneck. Course-fit: medium.**
4. **Calibration & selective prediction (abstention quality).** Less crowded than (1)–(3); concrete metrics (ECE, AURC, risk–coverage curves). Ties cleanly to the course's trustworthiness theme. **Open: yes (under-studied for fact-checking specifically). Tractable: yes. Course-fit: high.**
5. **Temporal drift & continual learning.** EvolveDetector and "What's Real News Today?" (Springer 2024) frame the problem; concept drift makes any deployed detector decay. **Open: yes. Tractable: medium — needs a longitudinal split. Course-fit: medium-high.**
6. **Multimodal misinformation.** MuMiN, Factify 2, MMM-Fact. Plenty of headroom but more engineering, more compute, and the data plumbing eats time. **Open: yes. Tractable: borderline. Course-fit: medium.**
7. **Cross-lingual / cross-domain transfer.** CheckThat!'s 20+ languages; lots of room. Compute-heavy at scale. **Open: yes. Tractable: borderline. Course-fit: medium.**

#### Top-of-mind recommended angles for this team

- **Primary: "LLM-vs-LLM" robustness with calibrated abstention.** Combine angle (1) and angle (4): build a RAG verifier that is explicitly evaluated against (i) human-written fakes, (ii) LLM-paraphrased fakes, (iii) LLM-from-scratch fakes, with **selective prediction** measured by a risk–coverage curve. Pairs with a "Virtual Hacker" generator (per the course PDF). This is the most defensible thesis.
- **Secondary: retrieval-failure-aware fact-checking.** Use MMM-Fact / AVeriTeC-2's stratified retrieval difficulty to study where RAG fact-checkers break, and propose a method that abstains when evidence is insufficient. Slightly narrower than the primary but cleaner experiments.
- **Tertiary: numerical-claim verification with claim decomposition.** CheckThat! 2025 Task 3 is fresh and under-saturated; small team can submit to CheckThat! 2026.

---

## Part B — Phase 1 plan

### B.1 Time-box

**14 calendar days, hard.** Day 15 the angle is locked and Phase 2 starts.

### B.2 Roles (2–4 people)

- **Survey lead** — drives the literature matrix, owns the decision document.
- **Probe engineer(s)** — runs the hands-on probes in week 2.
- **Critic** — reads everything the others write; argues against the leading candidate. Rotates.

### B.3 Workstream

#### Week 1 — Survey

Day 1–2 — **Read the four anchor surveys** (A.1) and skim the FEVER 2025 workshop proceedings (ACL Anthology volume `2025.fever-1`). Each person submits a one-page summary.

Day 3–5 — **Build the literature matrix** (`docs/phase-1/literature-matrix.csv`) with columns:

```
paper_id, title, venue, year, problem, method, dataset, headline_metric,
stated_limitation, our_one_line_takeaway, angle_tags, relevance_score (1-5)
```

Target: **30 papers minimum**, biased to 2024–2026. Sources to mine systematically:
- ACL/EMNLP/NAACL 2024–2025, NeurIPS 2024, FEVER workshop 2024 + 2025, CheckThat! 2024 + 2025 overviews on CEUR-WS, recent arXiv (search: "fact verif", "misinformation", "AVeriTeC", "claim verification").
- Two curated lists: [Cartus/Automated-Fact-Checking-Resources](https://github.com/Cartus/Automated-Fact-Checking-Resources) and [ICTMCG/LLM-for-misinformation-research](https://github.com/ICTMCG/LLM-for-misinformation-research).

Day 6–7 — **Cluster the limitations** column. Recurring complaints become candidate angles. Critic challenges each. Output: ≤ 5 candidate angles, each with a one-paragraph problem statement, the strongest existing baseline, and the "why isn't this solved already" explanation.

#### Week 2 — Hands-on probes

For each shortlisted angle, **half a day of code, no more**. Goal is to *see the failure mode*, not to solve anything. Reuse `misinfo.config`, `misinfo.repro`, `misinfo.logging` from Phase 0.

Standard probe shape:

1. Pick a public model from HuggingFace (DeBERTa-v3-MNLI for NLI, an open-weight 7–8 B LLM via `transformers` or a hosted endpoint for verifier).
2. Pick a public eval slice (AVeriTeC dev, FEVER dev, or MuMiN small).
3. Run the baseline on the slice + a perturbed slice that probes the angle. Examples:
   - **Angle 1 (LLM-generated fakes):** generate paraphrases of the same claims with a 7 B open-weight model; measure F1 delta.
   - **Angle 2 (retrieval failure):** swap in noisier/empty evidence; measure verdict change rate.
   - **Angle 4 (calibration):** plot a reliability diagram, compute ECE.
   - **Angle 5 (drift):** time-order AVeriTeC by claim date, train on early, test on late.
4. Record numbers in `docs/phase-1/probes/<angle>.md`.

Day 12 — **Bake-off meeting.** 30 minutes, each angle gets 3 minutes. Score each on (open / tractable / course-fit / our enthusiasm) on 1–5. Critic argues against the leader. Pick.

Day 13 — **Draft the decision document** ([docs/phase-1/DECISION.md](docs/phase-1/DECISION.md)) — see B.5 for structure.

Day 14 — **Office hours review** with the professor. Adjust scope based on feedback. Lock.

### B.4 Files this phase will create

```
docs/phase-1/
├── literature-matrix.csv            # the 30+ paper survey
├── README.md                        # how to navigate this folder
├── probes/
│   ├── angle-1-llm-fakes.md
│   ├── angle-2-retrieval-failure.md
│   ├── angle-4-calibration.md
│   └── ...
└── DECISION.md                      # the deliverable
```

Probe code lives in `notebooks/phase-1/` (exploratory) and any reusable bits get promoted into `src/misinfo/probes/` only if they survive into Phase 5 — most won't.

### B.5 The decision document — required structure

`docs/phase-1/DECISION.md` should be **≤ 4 pages** and contain exactly:

1. **The chosen angle** — one paragraph.
2. **Why it's open** — citations to the strongest existing work and what they don't solve.
3. **Hypothesis** — one falsifiable sentence. ("Adding insufficient-evidence abstention reduces high-confidence wrong verdicts on AVeriTeC-2 by ≥ X% without dropping coverage below Y%.")
4. **Proposed method (sketch)** — one paragraph; details deferred to Phase 4.
5. **Datasets and metrics** — primary + at least one robustness slice.
6. **Rejected alternatives** — one paragraph each, with the reason for rejection. This is the bit Phase 7's "threats to validity" later refers to.
7. **Risk register** — top 3 risks (compute, data access, scope creep) and the mitigation.
8. **Go/no-go decision** signed off by all team members + (separately) by the professor.

### B.6 Exit criteria (all must hold)

- Literature matrix has ≥ 30 entries, ≥ 60% from 2024–2026.
- Probes ran for ≥ 3 candidate angles and the failure mode is *visible in the numbers*, not just in someone's head.
- `DECISION.md` is committed on `dev`.
- The professor has acknowledged the chosen angle in office hours (a Teams message back is fine; we keep a screenshot/email in `docs/phase-1/professor-signoff.md`).

### B.7 Risks specific to Phase 1

- **Reading without writing.** Strict rule: every paper enters the matrix the day it's read. No "I'll add notes later."
- **Falling in love with the first angle.** That's why the critic role rotates and the bake-off is timed.
- **Probe rabbit holes.** Half a day per probe, hard cap. If the failure mode isn't visible by then, that itself is data — it usually means the angle is harder than it looks.
- **Compute access.** Confirm before week 2 that we can run a 7–8 B open-weight model somewhere (local GPU, Colab Pro, university cluster). If not, bias probes to encoder-scale models.

---

## Part C — Bibliography (live; expand during the phase)

Initial seed list, all verified during scouting:

- Chen, Shu (2024). [Combating Misinformation in the Age of LLMs](https://onlinelibrary.wiley.com/doi/10.1002/aaai.12188). *AI Magazine*.
- Eldifrawi et al. (2024). [Generative LLMs in Automated Fact-Checking: A Survey](https://arxiv.org/abs/2407.02351).
- "Hallucination to Truth" (2025). [arXiv:2508.03860](https://arxiv.org/abs/2508.03860) / Springer.
- Quelle, Bovet (2024). [The perils and promises of fact-checking with LLMs](https://pmc.ncbi.nlm.nih.gov/articles/PMC10879553/).
- DeVerna et al. (2024). [Fact-checking information from LLMs can decrease headline discernment](https://www.pnas.org/doi/10.1073/pnas.2322823121). *PNAS*.
- Schlichtkrull et al. (2024). [AVeriTeC: A Dataset for Real-world Claim Verification with Evidence from the Web](https://www.semanticscholar.org/paper/767f2f4f22c4f87d6f3a948596f36e4c4c5f1ad4).
- [The 2nd AVeriTeC Shared Task (FEVER 2025)](https://aclanthology.org/2025.fever-1.15/).
- Team HUMANE (2025). [HerO 2 for Efficient Fact Verification](https://arxiv.org/html/2507.11004).
- AIC CTU (2025). [Long-context RAG for FEVER 8](https://arxiv.org/html/2508.04390).
- [CLEF-2025 CheckThat! Lab Overview](https://arxiv.org/html/2503.14828v1).
- Wu et al. (2024). [SheepDog: style-agnostic fake news detection].
- *Nature Communications* (2025). [Linguistic features of AI mis/disinformation and the detection limits of LLMs](https://www.nature.com/articles/s41467-025-67145-1).
- Chen (2024). [Can LLM-Generated Misinformation Be Detected?](https://openreview.net/forum?id=ccxD4mtkTU)
- [Faithfulness-Aware Uncertainty Quantification for RAG Fact-Checking](https://arxiv.org/html/2505.21072) (2025).
- [MMM-Fact](https://arxiv.org/html/2510.25120) (2025).
- Drift (ACL 2025). [Enhancing LLM Faithfulness in Rationale Generation](https://aclanthology.org/2025.acl-long.340.pdf).
- HalluTree (2025). [Explainable Multi-Hop Hallucination Detection](https://aclanthology.org/2025.newsum-main.9.pdf).
- OpenFactCheck (2024). [arXiv:2405.05583](https://arxiv.org/abs/2405.05583).
- Nielsen, McConville (2022). [MuMiN](https://arxiv.org/abs/2202.11684).
- "What's Real News Today?" (Springer 2024) — multimodal continual learning.
- EvolveDetector (2024) — continual fake news detection.
- Hu et al. (2024). ARG / ARG-D — LLM-rationale distillation for small detectors.

This list is the *seed*; the matrix in B.3 will be ~30+ by end of week 1.
