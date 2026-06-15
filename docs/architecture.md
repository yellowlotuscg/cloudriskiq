# Architecture

> Initial draft for the Task 1 scaffold. Expect refinement as features land.

## Goal

Aggregate security findings from multiple sources into one normalized,
risk-scored, queryable view — so a small team can see "what should I fix first?"
across cloud, endpoint, and source control without logging into four consoles.

## High-level components

```
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │   AWS data   │   │  Azure data  │   │ Endpoint data│   │  GitHub data │
   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
          │                  │                  │                  │
          └──────────────────┴───────┬──────────┴──────────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │   Ingestion adapters     │  normalize → common model
                         │   (one per source)       │
                         └────────────┬─────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │   Risk scoring engine    │  severity + context → score
                         └────────────┬─────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │   Control mapper         │  category → NIST/CIS/PCI/SOX/FISMA
                         └────────────┬─────────────┘
                                      ▼
   ┌──────────────┐        ┌─────────────────────────┐        ┌──────────────┐
   │  Evidence    │◀──────▶│      FastAPI backend     │◀──────▶│  Next.js UI  │
   │  exporter    │        │  /findings /controls ... │        │  dashboard   │
   │ (JSON + MD)  │        └─────────────────────────┘        └──────────────┘
   └──────────────┘          (in-memory store; Postgres provisioned for later)
```

## Components

| Component | Responsibility | Status |
| --- | --- | --- |
| **FastAPI backend** | HTTP API: findings, summary, controls, evidence | ✅ implemented |
| **Ingestion adapters** | Parse source findings → common model | ✅ aws, azure, github, endpoint |
| **Risk scoring engine** | Combine severity + context into a 0–100 score | ✅ implemented |
| **Control mapper** | Finding category → NIST CSF / CIS / PCI / SOX / FISMA | ✅ implemented |
| **Evidence exporter** | Audit pack (JSON + Markdown) from live state | ✅ implemented |
| **In-memory store** | Hold findings + dashboard/coverage rollups | ✅ implemented |
| **CLI** | `ingest` / `report` / `evidence` from the terminal | ✅ implemented |
| **Next.js frontend** | Dashboard: KPIs, findings, control coverage | ✅ implemented |
| **PostgreSQL** | Persist normalized findings + history | provisioned in compose; not yet wired |

## Runtime topology

- Local dev: `uvicorn` for the API, `next dev` for the UI, optional local Postgres.
- Compose: three services — `db`, `backend`, `frontend` — on one network.
- `/health` deliberately has **no** external dependencies so liveness checks
  succeed even when the database is down.

## Key decisions (so far)

- **Normalize early.** Adapters convert source-specific shapes into one model at
  ingest time; the rest of the system only ever sees normalized findings.
- **Keep it runnable.** Every task leaves the app bootable and `/health` green.
- **Sample data first.** Adapters read `sample-data/` before any live API
  integration, so the pipeline is testable offline.
