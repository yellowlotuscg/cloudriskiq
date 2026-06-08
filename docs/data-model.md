# Data model

> Draft. The normalized schema is finalized in the next task; this captures the
> intended shape so adapters and the API agree.

## The normalized `Finding`

Every source is mapped to one common record:

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string (PK) | Stable, namespaced (e.g. `aws-0001`). |
| `source` | enum | `aws` \| `azure` \| `endpoint` \| `github`. |
| `external_id` | string | Original ID from the source system. |
| `title` | string | Short human-readable description. |
| `description` | text | Optional detail. |
| `severity` | enum | `low` \| `medium` \| `high` \| `critical`. |
| `resource` | string | Affected resource identifier (ARN, host, repo, …). |
| `resource_type` | string | e.g. `s3`, `iam`, `storageAccount`, `host`, `repo`. |
| `location` | string | Region / cloud location / N/A. |
| `risk_score` | int | 0–100, computed by the scoring engine. |
| `status` | enum | `open` \| `acknowledged` \| `resolved` \| `suppressed`. |
| `first_seen` | timestamptz | When the finding first appeared. |
| `last_seen` | timestamptz | Most recent ingest that still reports it. |
| `raw` | jsonb | The original source payload (for audit/debug). |
| `tags` | jsonb | Arbitrary key/value labels. |

## Severity → base score (starting point)

| Severity | Base score |
| --- | --- |
| low | 25 |
| medium | 50 |
| high | 75 |
| critical | 90 |

The scoring engine will adjust the base by context (public exposure, asset
criticality, age, exploitability) to produce the final `risk_score`.

## Relationships (anticipated)

- `Source` (one) → `Finding` (many).
- `Finding` (one) → `FindingEvent` (many): an append-only history of state
  changes (seen, acknowledged, resolved) for auditability.

## Why `raw` is kept

Storing the original payload as `jsonb` means new fields a source adds don't
require a migration to retain — adapters can backfill normalized columns later.
