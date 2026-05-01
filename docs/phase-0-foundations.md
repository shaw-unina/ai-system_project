# Phase 0 — Foundations: Decisions

First ADR-style note. Captures the choices made while bootstrapping the repo.

## Decisions

- **Environment manager: conda** (channel `conda-forge`, Python 3.11). Native-heavy libs install cleanly; pip-only deps live in `pyproject.toml` and are installed via `pip install -e .[dev]` from inside the conda env.
- **Package layout: src layout** under `src/misinfo/`, importable as `misinfo` after editable install. Build backend: setuptools.
- **Typed config: `pydantic-settings`** (`misinfo.config.Settings` + cached `get_settings()`). Sources priority: process env > `.env` > defaults. `.env` is gitignored.
- **Reproducibility utilities: `misinfo.repro`** — `seed_everything`, `hash_file`, `hash_dir`, `git_sha`. Torch seeding deferred until torch is introduced.
- **Logging: loguru**, level driven by `Settings.log_level`.
- **Docker: multi-stage** (`continuumio/miniconda3` builder → runtime). Smoke-test `CMD` until the FastAPI service exists in Phase 8. `docker-compose.yml` provides a single `app` service with `data/` and `models/` volume mounts.
- **Tooling: ruff + mypy + pytest**, configured in `pyproject.toml`.

## Explicitly deferred

- Dependency pinning tooling (pip-tools / `requirements.in` → compiled `requirements.txt`).
- Pre-commit hooks.
- CLI entry point (Typer placeholder).
- MLflow, DVC, PyTorch, Hugging Face stack — added when the phase that needs them lands.
- CI workflows, remote artifact stores, frontend.

## Verification (executed)

- `pytest -q` — passes.
- Package imports: `python -c "import misinfo; print(misinfo.__version__)"` — works.
- Docker build available via `docker compose build` (run on demand; not part of automated checks yet).
