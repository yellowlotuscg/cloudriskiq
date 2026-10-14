# Data model

> The running model is the Pydantic `Finding` in `backend/app/models.py`. The API keeps findings in memory. Postgres tables are not created yet.

## The normalized `Finding`

Every source is mapped to one common record:

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable, namespaced (e.g. `aws-0001`). The store is an in-memory dict, not a database table. |
| `source` | enum | `aws` \| `azure` \| `endpoint` \| `github`. |
| `external_id` | string | Original ID from the source system. |
| `title` | string | Short human-readable description. |
| `severity` | enum | `low` \| `medium` \| `high` \| `critical`. |
| `category` | enum | Adapter classification. The control mapper keys off this. |
| `resource` | string | Affected resource identifier (ARN, host, repo, …). |
| `resource_type` | string | e.g. `s3`, `iam`, `storageAccount`, `host`, `repo`. |
| `location` | string | Region / cloud location / N/A. |
| `risk_score` | int | 0-100, computed by the scoring engine. |
| `status` | enum | `open` \| `acknowledged` \| `resolved` \| `suppressed`. |
| `public_exposure` | bool | Scoring input. Set by the adapter. |
| `asset_criticality` | string | `low` \| `medium` \| `high`. Scoring input. |
| `exploit_signal` | bool | Scoring input. Known CVE, leaked secret, open admin port, and similar. |
| `compliance_scope` | list of string | `pci` \| `sox` \| `fisma`. Regulatory controls attach only when listed. |
| `first_seen` | string | ISO-8601 UTC. When the finding first appeared. |
| `last_seen` | string | ISO-8601 UTC. Defaults to `first_seen` when the sample omits it. |
| `controls` | list | Filled by the control mapper. Each item has `framework`, `control_id`, and `title`. |
| `raw` | object | The original source payload (for audit/debug). |
| `tags` | object | Arbitrary key/value labels. |

## Severity → base score (starting point)

| Severity | Base score |
| --- | --- |
| low | 25 |
| medium | 50 |
| high | 75 |
| critical | 90 |

`backend/app/scoring.py` adds context on top of that base: public exposure, asset criticality, exploit signal, compliance scope, and age. The result is clamped to 0-100.

## Relationships

- One source file maps to many `Finding` records. There is no separate `Source` table.
- A `FindingEvent` history (who changed a status, and when) is not implemented. Status updates overwrite the in-memory finding.

## Why `raw` is kept

The original payload stays on the finding so a new source field is still available for review. Nothing persists it to Postgres yet.
