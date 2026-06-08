# CloudRiskIQ

A unified security-findings aggregator. CloudRiskIQ ingests findings from
multiple sources — **AWS**, **Azure**, **endpoint** agents, and **GitHub** —
normalizes them into a common model, scores risk, and surfaces prioritized
issues through an API and a web dashboard.

> **Status:** Task 1 scaffold. The backend exposes a working `/health` endpoint
> with a passing test. Ingestion, scoring, persistence, and the dashboard land
> in later tasks. The app is intended to stay runnable after every feature.

## Tech stack

| Layer | Choice |
| --- | --- |
| Backend API | FastAPI (Python 3.12) |
| Frontend | Next.js / React (App Router, TypeScript) |
| Database | PostgreSQL 16 |
| Orchestration | Docker Compose |
| CI | GitHub Actions |

## Repository layout

```
cloudriskiq/
├── backend/            # FastAPI service (app/, tests/, Dockerfile, requirements.txt)
├── frontend/           # Next.js app (app/, Dockerfile, package.json)
├── sample-data/        # placeholder findings: aws/ azure/ endpoint/ github/
├── docs/               # architecture, data-model, api, security-model, resume-bullets
├── .github/workflows/  # backend-tests, frontend-tests
├── docker-compose.yml  # db + backend + frontend
├── .env.example
└── README.md
```

## Quick start

### Backend only (no Docker needed)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify the health endpoint:

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"cloudriskiq-api","version":"0.1.0","environment":"development"}
```

Interactive API docs: <http://localhost:8000/docs>

### Run the backend tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest -q          # includes the /health test
```

### Full stack with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

- Backend → <http://localhost:8000> (health at `/health`)
- Frontend → <http://localhost:3000> (shows live backend status)
- Postgres → `localhost:5432`

### Frontend only

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

## Documentation

- [Architecture](docs/architecture.md)
- [Data model](docs/data-model.md)
- [API](docs/api.md)
- [Security model](docs/security-model.md)
- [Résumé bullets](docs/resume-bullets.md)

## Roadmap (high level)

1. ✅ Scaffold: health endpoint, compose, CI, docs, sample-data placeholders.
2. Define the normalized finding model + Postgres schema and migrations.
3. Ingestion adapters per source (AWS, Azure, endpoint, GitHub) reading `sample-data/`.
4. Risk scoring + prioritized findings API.
5. Dashboard views (findings list, filters, severity, source breakdown).
