# Feature Flag & Experimentation Service — Take-Home (L7 Technical Manager)

Welcome! This is the starter kit for a 2-day take-home assignment aimed at a Level 7 Technical Manager. You’ll design and implement a **multi-tenant feature-flag & experimentation service** in Python.

You are expected to demonstrate **architecture & design**, **implementation excellence**, **testing strategy**, **reliability/observability**, **security & multi-tenancy**, **performance/data acumen**, and **delivery leadership & communication**.

> Timebox: ~2 working days. Must-haves are designed to be achievable within 12–16 hours. Stretch goals are optional.

---

## Quick Start

```bash
# a) Install Python version 3.11
brew install python@3.11
# 1) Local (no Docker) — requires Python 3.11+
python3.11 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip wheel
pip install -r requirements.txt -r requirements-dev.txt
make run      # starts the API on http://localhost:8000
make seed     # loads sample data
open http://localhost:8000/docs

# 2) Docker (optional, includes Postgres)
docker compose up --build
# app: http://localhost:8000, pg: localhost:5432 (user=postgres, pass=postgres)
```

**Health:** `GET /healthz` and `GET /readyz`  
**Metrics:** `GET /metrics` (Prometheus format)  
**OpenAPI:** `GET /openapi.json` and Swagger at `/docs`

---

## The Assignment (high level)

You’ll build a service that lets tenants manage flags and segments, and **evaluate a flag** for a specific (user, context) with rules and percentage rollouts. Provide JWT/token auth, tenant isolation, auditing of changes, and a fast in-memory evaluation path with caching.

See the full brief in `docs/brief.md`.

---

## Deliverables Checklist

- [ ] Working API with must-have endpoints
- [ ] Tests (unit + integration + at least one e2e happy path)
- [ ] Health/readiness endpoints, structured logs, metrics
- [ ] JWT/token auth, tenant isolation, input validation
- [ ] Basic data model & migrations/DDL (migrations optional)
- [ ] ADRs (1–3), risk log, stakeholder readout (templates provided)
- [ ] CI (lint, type check, test) and one-command dev flow (`make` targets)
- [ ] Brief “what I built / what I cut / what I’d do next” in README or `docs/`

---

## Repo Layout

```
app/
  main.py
  config.py
  deps.py
  models.py
  schemas.py
  utils/
    logging.py
    security.py
  services/
    cache.py
    flag_eval.py
    audit.py
  routers/
    health.py
    auth.py
    flags.py
    segments.py
    evaluate.py
    audit.py
docs/
  brief.md
  scoring-guide.md
  reviewer-checklist.md
  adr/0000-template.md
  stakeholder-readout-template.md
  risks-template.md
  api-sample.md
scripts/
  seed.py
  curl-examples.sh
tests/
  conftest.py
  test_health.py
  test_bucket_deterministic.py
Dockerfile
docker-compose.yml
Makefile
requirements.txt
requirements-dev.txt
.github/workflows/ci.yml
requests.http
```

---

## Notes

- Starter implements only scaffolding + a minimal evaluation path to let you run smoke tests. You’ll complete the core logic to satisfy the brief.
- You can stay on SQLite (default) or switch to Postgres via `DB_DSN` env.
- Use `X-Tenant-ID` header for tenant scoping. Protected endpoints require `Authorization: Bearer <JWT>`.
- Seed data includes a tenant `acme` and example flags/segments to test evaluation.

Good luck & have fun!
