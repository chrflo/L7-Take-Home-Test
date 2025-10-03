# Feature Flag & Experimentation Service — Full Brief

## Objective
Build a **multi-tenant Feature Flag & Experimentation Service** with:
- CRUD for **flags** and **segments**
- **Evaluate** a flag for a `(user, context)`
- **Percentage rollouts** and **targeting rules** (attributes/cohorts)
- **Tenant isolation**, **JWT auth**, and **audit log** of changes
- **Fast** evaluation path (in-memory cache) and **idempotent** writes
- **Health/readiness**, **structured logs**, **metrics**

Stretch (optional):
- Dry-run “preview” evaluation for hypothetical users
- Change events stream with simple retry for subscribers
- A minimal Python client SDK

> Timebox: focus on must-haves; stretch is optional and scored as “exceeds.”

---

## Must-Have Endpoints (suggested)

**Auth & Tenancy**
- `POST /v1/auth/token` — issue JWT for a known service/client (stub allowed)
- Header: `X-Tenant-ID: <tenant>` required for all protected routes

**Flags**
- `POST /v1/flags` — create flag (idempotent by key+tenant)
- `GET /v1/flags` — list with pagination & filters
- `GET /v1/flags/{key}` — retrieve by key
- `PUT /v1/flags/{key}` — update rules, variants, status
- `DELETE /v1/flags/{key}` — soft-delete recommended

**Segments**
- `POST /v1/segments` — create segment (e.g., cohorts)
- `GET /v1/segments` — list with pagination & filters
- `GET /v1/segments/{key}` — retrieve
- `PUT /v1/segments/{key}` — update
- `DELETE /v1/segments/{key}` — delete

**Evaluation**
- `POST /v1/evaluate` — body: `{ "flag_key": "...", "user": {"id": "...", "attributes": {...}} }`
  - Returns: `{ "variant": "...", "reason": "...", "rule_id": "...", "details": {...} }`
  - Apply: on/off, explicit allow/deny, segment matches, attribute matchers, and **percentage bucketing**.
  - **Deterministic** bucketing by `(tenant, flag_key, user_id)`.

**Audit & Ops**
- `GET /v1/audit` — filter by entity, flag_key, actor, time window
- `GET /healthz` and `GET /readyz`
- `GET /metrics` — prometheus format

---

## Data Model (suggested)

- **Flag**: `id, tenant_id, key (unique per tenant), description, state (on/off), variants [{key, weight}], rules [Rule], deleted_at, updated_at, created_at`
- **Rule** (embedded or separate): `id, order, expression (segment/attributes), rollout {weight or distribution}, constraints`
- **Segment**: `id, tenant_id, key, criteria (attributes list or cohort ids), updated_at, created_at`
- **Audit**: `id, tenant_id, actor, entity (flag/segment), entity_id, action, before, after, ts`

You may store rules/criteria as JSON for speed of delivery. Prefer indexes on `(tenant_id, key)`, `(tenant_id, ts)`.

---

## Security & Tenancy

- Require `Authorization: Bearer <JWT>` and `X-Tenant-ID` header for protected routes.
- JWT can be issued by a simple stub endpoint with a shared secret (HS256).
- Enforce per-tenant scoping on reads/writes and in evaluation.
- Validate inputs; keep secrets in env vars; use least-privileged defaults.

---

## Performance & Caching

- Use an in-memory cache of **compiled rules** keyed by `(tenant, flag_key)`.
- Cache invalidation on flag/segment change (push or TTL).
- Deterministic percentage bucketing via a stable hash → [0.0, 1.0).
- Consider hot paths: evaluation should be **sub-millisecond** in-memory.

---

## Observability & Reliability

- Structured JSON logs with correlation ids (pass through `X-Request-ID` if present).
- Metrics: request counts, latencies, cache hit/miss, evaluation outcomes.
- Timeouts/retries calling any external adapter (if you add one).
- Health vs Readiness: database connectivity, cache warm status, etc.

---

## Quality & Tests

- Unit tests for: rule matching, bucketing, idempotent create
- Integration test for: CRUD + evaluate happy path
- Optionally property-based tests for bucketing and rule evaluation

---

## Delivery & Communication

- 1–3 **ADRs** capturing the key choices (data store, cache invalidation, rules format).
- **Risk log** with top risks and mitigations.
- **Stakeholder readout** (one pager): problem, outcomes, risks, next steps.
- Open a self-PR and write review comments as if reviewing a peer’s work.

---

## Stretch Ideas

- `/v1/evaluate/preview` to test a hypothetical context
- Event stream: `/v1/events` (SSE or webhook retrier) for changes
- Minimal Python SDK (`flag_client.evaluate(flag_key, user)`)

---

## “Done” Criteria

- Must-have endpoints behave as specified
- Evaluation is deterministic, performant, and respects tenant scoping
- Meaningful tests pass in CI
- Clear documentation of trade-offs and next steps
