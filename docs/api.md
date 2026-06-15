# API

Base URL (local): `http://localhost:8000`
Interactive docs: `/docs` (Swagger UI), `/redoc`.

All endpoints below are implemented. The findings store is hydrated from
`sample-data/` at startup, so every endpoint returns data with no setup.

### `GET /health`

Liveness probe. No external dependencies.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "service": "cloudriskiq-api",
  "version": "0.1.0",
  "environment": "development"
}
```

### `GET /`

Service metadata.

```json
{ "name": "CloudRiskIQ API", "version": "0.1.0", "docs": "/docs" }
```

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

### Anticipated `/findings` response shape

```json
{
  "items": [
    {
      "id": "aws-0001",
      "source": "aws",
      "title": "S3 bucket allows public read",
      "severity": "high",
      "risk_score": 80,
      "status": "open",
      "resource": "arn:aws:s3:::example-public-bucket",
      "first_seen": "2026-06-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

## Conventions

- JSON request/response bodies.
- Severities: `low` · `medium` · `high` · `critical`.
- Timestamps are ISO-8601 UTC (`...Z`).
- Errors use standard HTTP status codes with a `{"detail": "..."}` body (FastAPI default).
