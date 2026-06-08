# Résumé bullets

Draft bullets describing CloudRiskIQ, to refine as the project grows. Keep them
honest — only claim what's actually built. Update as tasks complete.

## Current (after Task 1 scaffold)

- Designed and scaffolded **CloudRiskIQ**, a full-stack security-findings
  aggregator (FastAPI · Next.js/React · PostgreSQL · Docker Compose · GitHub
  Actions) that normalizes findings across AWS, Azure, endpoint, and GitHub
  into one risk-scored view.
- Stood up a containerized three-service architecture (API, web, Postgres) with
  a dependency-free `/health` liveness endpoint and CI test workflows from day
  one, keeping the app runnable after every change.

## To unlock as features land (don't claim until true)

- Built source-specific ingestion adapters normalizing heterogeneous findings
  into a common model persisted in PostgreSQL.
- Implemented a risk-scoring engine combining severity with context (public
  exposure, asset criticality, age) to prioritize remediation.
- Delivered a Next.js dashboard with filtering by source/severity/status and
  at-a-glance risk summaries.
- Added automated tests and GitHub Actions CI (backend pytest + frontend build),
  achieving _N%_ coverage.

## Phrasing tips

- Lead with the verb and the impact, not the tech list.
- Quantify when you can (sources integrated, findings processed, latency).
- One bullet = one accomplishment.
