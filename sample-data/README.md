# sample-data

**Synthetic placeholder findings** used for local development and tests. None of
this is real data; IDs, accounts, and resources are fabricated.

Each source has a `findings.sample.json` with an illustrative shape. Later tasks
add per-source ingestion adapters that read these files, normalize them into the
common finding model (see [../docs/data-model.md](../docs/data-model.md)), and
persist them.

```
sample-data/
├── aws/findings.sample.json       # S3, IAM, ...
├── azure/findings.sample.json     # Storage, NSG, ...
├── endpoint/findings.sample.json  # EDR / device posture
└── github/findings.sample.json    # secret scanning, Dependabot
```

Severities use a common scale: `low` · `medium` · `high` · `critical`.
