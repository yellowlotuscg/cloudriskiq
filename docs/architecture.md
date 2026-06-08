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
   ┌──────────────┐        ┌─────────────────────────┐        ┌──────────────┐
   │  PostgreSQL  │◀──────▶│      FastAPI backend     │◀──────▶│  Next.js UI  │
   │  (findings)  │        │  /health, /findings, ... │        │  dashboard   │
   └──────────────┘        └─────────────────────────┘        └──────────────┘
```

## Components

| Component | Responsibility | Status |
| --- | --- | --- |
| **FastAPI backend** | HTTP API, scoring, persistence access | `/health` live |
| **Ingestion adapters** | Pull/parse source findings → common model | planned |
| **Risk scoring engine** | Combine severity + context into a score | planned |
| **PostgreSQL** | Store normalized findings + history | provisioned in compose |
| **Next.js frontend** | Dashboard: list, filter, prioritize | skeleton |

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
