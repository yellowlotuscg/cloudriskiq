# API

Base URL (local): `http://localhost:8000`
Interactive docs: `/docs` (Swagger UI), `/redoc`.

All endpoints below are implemented. Run from a checkout of this repo and the API loads `sample-data/` at startup. The backend container does not include that directory, so those routes come back empty there. See the README.

### `GET /health`

Liveness probe. No external dependencies.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "service": "cloudriskiq-api",
  "version": "0.2.0",
  "environment": "development"
}
```

### `GET /`

Service metadata.

```json
{
  "name": "CloudRiskIQ API",
  "version": "0.2.0",
  "docs": "/docs",
  "findings_loaded": 19
}
```

`findings_loaded` is how many findings ingest placed in memory at startup. With the sample files in this repo, that count is 19.

## Findings, rollups, and compliance

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/findings` | List findings (highest risk first); filters: `source`, `severity`, `status`, `min_score`. |
| `GET` | `/findings/{id}` | Single finding with its full control mapping. |
| `PATCH` | `/findings/{id}?status=...` | Update `status` (acknowledge / resolve / suppress). |
| `GET` | `/summary` | Counts by source / severity / status / category, plus avg risk and top findings. |
| `GET` | `/controls` | Control coverage: findings rolled up per NIST CSF / CIS / PCI / SOX / FISMA control. |
| `GET` | `/evidence` | Structured control evidence pack (also available as Markdown via the CLI). |
| `POST` | `/ingest` | Re-run ingestion from `sample-data/` (re-reads, re-scores, re-maps). |

### `GET /findings` response shape

Each item is a full `Finding`. The list below is shortened. `risk_score` is computed at ingest from severity, context, and age, so the number changes as a finding gets older. Do not treat a sample number as a fixture.

```json
{
  "items": [
    {
      "id": "aws-0001",
      "source": "aws",
      "title": "S3 bucket allows public read",
      "severity": "high",
      "status": "open",
      "resource": "arn:aws:s3:::acme-prod-customer-exports",
      "first_seen": "2026-04-18T00:00:00Z"
    }
  ],
  "total": 1
}
```

## Conventions

- JSON response bodies. `PATCH /findings/{id}` takes `status` as a query parameter, not a JSON body.
- Severities: `low` · `medium` · `high` · `critical`.
- Timestamps are ISO-8601 UTC (`...Z`).
- Errors use standard HTTP status codes with a `{"detail": "..."}` body (FastAPI default).
