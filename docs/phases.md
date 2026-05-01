# Misinformation Detector — Project Phases

High-level phase plan for an LLM-based misinformation detection system, structured as a hybrid Innovation + Research effort. The plan targets an industry-grade deliverable: reproducible pipelines, evaluated trustworthiness properties, a deployable service, and a user-facing dashboard.

---

## Phase 0 — Foundations
- Repository scaffolding on the `dev` branch: package layout, Python env, dependency pinning, formatter/linter, typed config.
- Experiment tracking and artifact storage decided up front (e.g., MLflow / W&B, DVC or LFS for data/models).
- Reproducibility primitives: seed control, deterministic data splits, hashed dataset/model artifacts.
- Secrets and environment management (`.env`, never committed).

## Phase 1 — Research Scouting (time-boxed)
- Structured survey of fact-checking and misinformation literature (2023–2025), shared tasks (CheckThat!, FEVER, AVeriTeC), and current SOTA pipelines.
- Paper-tracking matrix: problem, method, dataset, metric, stated limitation.
- Cluster limitations into 3–5 candidate research angles; run a short hands-on probe per angle to verify the failure mode is real.
- **Deliverable:** decision document selecting one research angle with rejected alternatives recorded.

## Phase 2 — Problem Definition & Requirements
- Scope lock: input modality (text / news / posts / multimodal), language coverage, output contract (binary, calibrated probability, claim-level verdicts with evidence and rationale).
- Stakeholder model and target use case.
- Functional and non-functional requirements: accuracy, latency, calibration, fairness, robustness, explainability, privacy.
- Formal research hypothesis and quantitative success criteria.

## Phase 3 — Data Strategy
- Dataset selection (LIAR, FakeNewsNet, FEVER, AVeriTeC, MuMiN, CheckThat!, ISOT) with license and provenance review.
- **Time-ordered** splits to prevent temporal leakage; held-out drift slice.
- Ingestion + preprocessing pipeline as code (idempotent, versioned).
- Dataset cards documenting source, biases, limitations, intended use.

## Phase 4 — System Architecture
- Architecture options compared in writing: fine-tuned encoder baseline, retrieval-augmented LLM verifier, hybrid claim-extraction pipeline.
- Module boundaries: ingestion → claim extraction → evidence retrieval → verification → rationale → scoring → API.
- Tech stack and infrastructure choices (model runtime, vector store, serving layer, container strategy).
- Architecture Decision Records (ADRs) capturing each non-trivial choice and its trade-offs.

## Phase 5 — Baseline Implementation (Innovation)
- Strong reproducible baseline (e.g., fine-tuned encoder) with full evaluation harness: F1, AUC, ECE (calibration), per-slice metrics.
- Logged, comparable runs; baseline is the reference point every later experiment is measured against.

## Phase 6 — Proposed Method Implementation (Research)
- Implementation of the chosen research angle (e.g., robustness to LLM-generated misinformation, retrieval-failure handling, rationale faithfulness, selective prediction).
- Iterative development against the evaluation harness; ablations recorded.

## Phase 7 — Evaluation & Trustworthiness Assessment
- Controlled comparison vs. baseline: multiple seeds, statistical significance.
- Robustness suite: adversarial paraphrase, LLM-generated fakes, temporal drift, cross-domain transfer.
- Fairness slice analysis across topic, source, and language.
- Calibration and selective-prediction analysis (abstention quality).
- Documented threats to validity.

## Phase 8 — Service Layer & Local Deployment
- Inference service exposed via a typed HTTP API (FastAPI) with versioned schemas.
- Containerized deployment (Docker / Compose) suitable for local and on-prem.
- Structured logging, request tracing, basic metrics endpoint.
- Model registry pattern: load by version/hash, not by file path.

## Phase 9 — Continuous Monitoring & Quality Gates
- Drift and performance monitoring (input distribution, confidence distribution, slice metrics).
- Regression tests on a frozen evaluation set; CI runs them on every change.
- Quality gates before promotion: minimum accuracy, calibration, fairness deltas.
- Incident playbook for model regressions.

## Phase 10 — Frontend Dashboard *(next year)*
- User-facing dashboard to interact with the detector: submit claims/articles, view verdict, confidence, supporting/contradicting evidence, and rationale.
- Operator/analyst views: batch evaluation, slice metrics, drift signals, recent low-confidence cases.
- Auth and rate limiting where appropriate.
- Stack to be chosen at the start of this phase (likely Next.js or a lightweight React + Tailwind setup wired to the FastAPI service).

## Phase 11 — Hardening & Release
- Performance tuning (latency, throughput, memory footprint).
- Security review of the service surface (input validation, prompt-injection considerations for the LLM path, dependency scanning).
- Final documentation: architecture, model cards, evaluation report, operator guide, API reference.
- Tagged release with reproducible build artifacts.

---

## Cross-cutting tracks
- **Trustworthiness:** fairness, robustness, calibration, and explainability are evaluated continuously, not bolted on at the end.
- **Reproducibility:** every experiment is rerunnable from a commit + config + data hash.
- **Risk log:** label quality, temporal leakage, LLM/inference cost, scope of "truth" claims, model staleness.
- **Documentation:** ADRs, model cards, dataset cards, and the evaluation report evolve alongside the code.
