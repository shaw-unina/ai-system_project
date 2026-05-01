# syntax=docker/dockerfile:1.6

FROM continuumio/miniconda3:latest AS builder

WORKDIR /app

COPY environment.yml pyproject.toml README.md LICENCE ./
COPY src ./src

RUN conda env create -f environment.yml && conda clean -afy

FROM continuumio/miniconda3:latest AS runtime

ENV PATH=/opt/conda/envs/misinfo/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /opt/conda/envs/misinfo /opt/conda/envs/misinfo

RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /app

COPY --chown=app:app pyproject.toml README.md LICENCE ./
COPY --chown=app:app src ./src

CMD ["python", "-c", "import misinfo; print('misinfo', misinfo.__version__)"]
