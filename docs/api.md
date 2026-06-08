# API

Base URL (local): `http://localhost:8000`
Interactive docs: `/docs` (Swagger UI), `/redoc`.

## Implemented

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

## Planned

These are not implemented yet — listed so the contract is visible early.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/findings` | List findings; filters: `source`, `severity`, `status`, `min_score`. |
| `GET` | `/findings/{id}` | Single finding with full detail and history. |
| `PATCH` | `/findings/{id}` | Update `status` (acknowledge / resolve / suppress). |
| `POST` | `/ingest/{source}` | Trigger ingestion for a source (reads sample-data initially). |
| `GET` | `/stats` | Counts by source / severity / status for the dashboard. |

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
