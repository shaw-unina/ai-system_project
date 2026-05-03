.PHONY: api serve test cov compose-up compose-down perf-latency perf-throughput perf-memory

PY ?= /opt/anaconda3/envs/misinfo/bin/python

# Local non-Docker dev — auto-reload
api:
	$(PY) -m misinfo.cli serve --host 127.0.0.1 --port 8000 --reload

# Same, no reload (closer to prod)
serve:
	$(PY) -m misinfo.cli serve --host 0.0.0.0 --port 8000

test:
	$(PY) -m pytest

cov:
	$(PY) -m pytest --cov=src/misinfo --cov-report=term

compose-up:
	docker compose up --build

compose-down:
	docker compose down

perf-latency:
	$(PY) scripts/perf_bench.py latency --n 200

perf-throughput:
	$(PY) scripts/perf_bench.py throughput --n 100

perf-memory:
	$(PY) scripts/perf_bench.py memory --n 50
