# Security model

> Draft for the scaffold. CloudRiskIQ handles security findings, so the tool
> itself must be handled carefully — findings data is sensitive.

## Data sensitivity

Findings can reveal exploitable weaknesses (public buckets, open RDP, leaked
secrets). Treat the CloudRiskIQ database and API as **sensitive**: exposure of
the findings list is itself a security risk.

## Secrets handling

- No secrets in the repo. Configuration comes from environment variables; see
  [`.env.example`](../.env.example). `.env` is git-ignored.
- Source credentials (AWS keys, Azure service principals, GitHub tokens) will be
  injected via environment / a secrets manager — never committed.
- The `raw` payload stored per finding may contain sensitive strings; access to
  it is restricted to authenticated API consumers.

## AuthN / AuthZ (planned)

- API authentication via bearer tokens (service-to-service) and/or session auth
  for the dashboard. Not yet implemented in the scaffold.
- Role-based access: read-only viewer vs. responder (can change finding status).

## Network & transport

- TLS terminated at the edge in production (reverse proxy / load balancer).
- `CORS_ORIGINS` is explicit and defaults to the local frontend only.
- `/health` is unauthenticated by design (liveness only, no sensitive data).

## Input handling

- All source payloads are treated as untrusted input; adapters validate and
  normalize before persistence.
- Use parameterized queries / an ORM — never string-build SQL from finding data.

## Auditability

- A `FindingEvent` history (see [data-model](data-model.md)) records state
  changes for an audit trail of who acknowledged/resolved what and when.

## Out of scope (for now)

- Multi-tenant isolation.
- Encryption-at-rest configuration (delegated to the database/host).

## Threat-model checklist (to revisit each task)

- [ ] No secret committed to git.
- [ ] New endpoints require auth unless explicitly public.
- [ ] New stored fields reviewed for sensitivity.
- [ ] Dependencies scanned (Dependabot / CI).
