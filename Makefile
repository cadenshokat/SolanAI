# ---- Project settings ----
PROJECT ?= solanai
IMAGE   ?= $(PROJECT):latest
COMPOSE ?= docker compose
PY      ?= python
PIP     ?= pip

# ---- Help ----
.PHONY: help
help:
	@echo "Targets:"
	@echo "  install           Create venv & install deps"
	@echo "  run               Run API locally (dev server)"
	@echo "  run-worker        Run background scheduler locally"
	@echo "  routes            Print Flask routes"
	@echo "  docker-build      Build Docker image(s)"
	@echo "  docker-up         Start api + worker (detached)"
	@echo "  docker-down       Stop all containers"
	@echo "  docker-logs       Tail logs for api & worker"
	@echo "  docker-shell      Open a shell in api container"
	@echo "  clean             Remove caches & __pycache__"

# ---- Local (no docker) ----
.PHONY: install install-dev
install:
\tpip install .

install-dev:
\tpip install -e .[dev]

.PHONY: run
run:
	$(PY) run.py

.PHONY: run-worker
run-worker:
	$(PY) -m worker.runner

.PHONY: routes
routes:
	$(PY) - <<'PY'
from app import create_app
app = create_app()
for r in app.url_map.iter_rules():
    print(f"{r:40s} -> {r.endpoint}")
PY

# ---- Docker ----
.PHONY: docker-build
docker-build:
	$(COMPOSE) build --pull

.PHONY: docker-up
docker-up:
	$(COMPOSE) up -d

.PHONY: docker-down
docker-down:
	$(COMPOSE) down

.PHONY: docker-logs
docker-logs:
	$(COMPOSE) logs -f --tail=200 api worker

.PHONY: docker-shell
docker-shell:
	$(COMPOSE) exec api bash

# ---- Housekeeping ----
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
