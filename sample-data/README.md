# sample-data

Synthetic findings for local development and tests. IDs, accounts, and resources are made up. Nothing here is from a real account.

Each source has a `findings.sample.json`. The adapters in `backend/app/adapters/` read these files, normalize them into the common finding model (see [../docs/data-model.md](../docs/data-model.md)), score them, and map controls. The API keeps the result in memory. Nothing is written back to these files.

```
sample-data/
├── aws/findings.sample.json       # S3, IAM, ...
├── azure/findings.sample.json     # Storage, NSG, ...
├── endpoint/findings.sample.json  # EDR / device posture
└── github/findings.sample.json    # secret scanning, Dependabot
```

Severities use a common scale: `low`, `medium`, `high`, `critical`.
