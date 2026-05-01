# Misinformation Detector

LLM-based misinformation detection system. AI Systems Engineering course project (Prof. Pietrantuono).

See [docs/phases.md](docs/phases.md) for the full phase plan and [docs/phase-0-foundations.md](docs/phase-0-foundations.md) for Phase 0 decisions.

## Quickstart (conda)

```bash
conda env create -f environment.yml
conda activate misinfo
cp .env.example .env   # then edit
pytest -q
```

The package installs in editable mode automatically via `environment.yml`. After activation, `import misinfo` works from anywhere.

## Quickstart (Docker)

```bash
docker compose build
docker compose run --rm app
```

The `app` service runs a smoke test (`import misinfo`) until the FastAPI service arrives in Phase 8.

## Configuration

Settings are loaded by `misinfo.config.get_settings()` from (in priority order) process env, `.env`, then defaults. `.env` is gitignored — never commit secrets.

## Reproducibility

`misinfo.repro` provides:
- `seed_everything(seed)` — seeds `random`, `numpy`, and `PYTHONHASHSEED`.
- `hash_file(path)` / `hash_dir(path)` — sha256 fingerprints for data/model artifacts.
- `git_sha()` — current commit, for run metadata.

## Project layout

```
.
├── docs/                 Phase plan and decision records
├── data/                 raw / interim / processed / external (gitignored when sensitive)
├── models/               Trained model artifacts (gitignored)
├── notebooks/            Exploratory notebooks
├── references/           Briefs, papers, manuals
├── reports/              Generated analysis and figures
├── src/misinfo/          Importable package (config, repro, logging, modeling, services)
├── tests/                Pytest suite
├── environment.yml       Conda environment
├── pyproject.toml        Build, deps, tool config
├── Dockerfile            Multi-stage build (builder → runtime)
└── docker-compose.yml    Local deployment
```
