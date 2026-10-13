# Security model

> Draft for the scaffold. CloudRiskIQ handles security findings, so the tool
> itself must be handled carefully; findings data is sensitive.

## Data sensitivity

Findings can reveal exploitable weaknesses (public buckets, open RDP, leaked
secrets). Treat the CloudRiskIQ database and API as **sensitive**: exposure of
the findings list is itself a security risk.

## Secrets handling

- No secrets in the repo. Configuration comes from environment variables; see
  [`.env.example`](../.env.example). `.env` is git-ignored.
- Source credentials (AWS keys, Azure service principals, GitHub tokens) will be
  injected via environment / a secrets manager, never committed.
- The `raw` payload on a finding may contain sensitive strings. The API has no authentication, so `GET /findings` and `GET /findings/{id}` return `raw` to anyone who can reach the process. Do not point this demo at real findings.

## AuthN / AuthZ (planned)

- API authentication via bearer tokens (service-to-service) and/or session auth
  for the dashboard. Not implemented.
- Role-based access: read-only viewer vs. responder (can change finding status).

## Network & transport

- TLS terminated at the edge in production (reverse proxy / load balancer).
- `CORS_ORIGINS` is explicit and defaults to the local frontend only.
- `/health` is unauthenticated by design (liveness only, no sensitive data).

## Input handling

- All source payloads are treated as untrusted input. Adapters normalize them before they go into the in-memory store.
- Use parameterized queries / an ORM; never string-build SQL from finding data.

## Auditability

- A `FindingEvent` history is not built. `PATCH /findings/{id}` overwrites status in memory and keeps no record of who changed it. See [data-model](data-model.md).

## Out of scope (for now)

- Multi-tenant isolation.
- Encryption-at-rest configuration (delegated to the database/host).

## Threat-model checklist (to revisit each task)

- [ ] No secret committed to git.
- [ ] New endpoints require auth unless explicitly public.
- [ ] New stored fields reviewed for sensitivity.
- [ ] Dependencies scanned (Dependabot / CI).
