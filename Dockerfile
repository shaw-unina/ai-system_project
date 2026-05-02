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

USER root
RUN pip install --no-deps -e '.[inference,service]'
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://localhost:8000/healthz', timeout=3).status==200 else 1)"

CMD ["misinfo", "serve", "--host", "0.0.0.0", "--port", "8000"]
