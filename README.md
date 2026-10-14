# CloudRiskIQ

A case study from [Yellow Lotus Consulting Group](https://yellowlotuscg.com). It is a security and compliance tool built on synthetic data, not client data.

My background is IT operations, security, and audit support. I was the primary technical contact for SOX, PCI-DSS, and FISMA audits, the person who had to turn a pile of scanner output into "here's the control, here's the evidence, here's what we're fixing first." CloudRiskIQ is the tool I wanted during those audits.

It ingests security findings from **AWS, Azure, endpoints, and GitHub**, normalizes them into one model, scores each one by *risk* (not just raw severity), and maps every finding to the controls it touches across **NIST CSF 2.0, CIS Controls v8, PCI-DSS v4.0, SOX ITGC, and FISMA / NIST 800-53**. It writes a structured evidence pack from the demo state for a person to review. Control mappings are illustrative and require validation against the applicable standard and organizational scope; this tool does not certify compliance.

You can run the API, the CLI, and the dashboard on a laptop from `sample-data/`. No cloud credentials, and no database. Docker Compose mounts those same files into the API container. See [Full stack with Docker Compose](#full-stack-with-docker-compose).

> **Heads up:** all sample findings are synthetic. No real accounts, resources, or secrets are in this repo.

---

## What I broke / fixed / built

Recruiters keep saying the same thing: skip the cert wall, show me that you broke something, fixed something, and built something, and show me how you think. So, plainly:

- **Broke:** In real audits I watched teams drown in raw scanner output. A console full of "HIGH" findings tells you nothing about *what to fix first*. A HIGH on a public, production, cardholder-data bucket is not the same risk as a HIGH on an internal dev box, but the scanner scores them identically. And when the auditor asked "which control does this map to, and show me the evidence," that traceability lived in someone's spreadsheet, by hand.
- **Fixed:** I built a transparent risk-scoring engine that adjusts severity by context (public exposure, asset criticality, exploit signal, compliance scope, age) so the list sorts by *what actually matters*. And I built a control mapper that turns every technical finding into framework references automatically, so the "map it to a control + produce evidence" step isn't manual anymore.
- **Built:** A working full-stack app. FastAPI backend (ingestion adapters, scoring, control mapping, evidence export), a Next.js dashboard, a CLI, and a test suite. See the full writeup in [docs/broke-fixed-built.md](docs/broke-fixed-built.md).

---

## What it demonstrates (mapped to my background)

| In this repo | From my résumé |
| --- | --- |
| Control mapping to NIST CSF / CIS / PCI / SOX / FISMA | Primary contact for SOX/PCI-DSS/FISMA audits; CIS/NIST CSF hardening |
| Risk-scoring engine that prioritizes remediation | Remediated 450+ SOX findings, where prioritization was the whole game |
| Python evidence-pack generator (JSON + Markdown) | Built Python/PowerShell evidence-collection tooling for audits |
| Normalized ingestion across AWS / Azure / GitHub / endpoint | Cloud security posture + vuln management (Qualys) across estates |
| Git-versioned, test-covered, CI-checked code | Git-versioned auditable configs; control dashboards |

---

## Quick start

```bash
git clone https://github.com/yellowlotuscg/cloudriskiq.git
cd cloudriskiq
```

### Backend + CLI (no Docker, no database)

Use Python 3.12. That is what CI and the backend image use. Run these from `backend/` so `python -m app...` can import the package.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The API holds the terminal. Swagger UI is at http://localhost:8000/docs.

```bash
uvicorn app.main:app --reload --port 8000
```

The CLI uses the same engine and does not need the API process. Run it from `backend/` with the virtualenv activated:

```bash
python -m app.cli ingest
python -m app.cli report
python -m app.cli evidence
```

`ingest` loads and scores the sample files and prints a summary. `report` prints the prioritized table. `evidence` writes `evidence-pack.json` and `evidence-pack.md` under `./evidence-out` (gitignored). Pass `--out` to use another directory.

On startup the API reads `SAMPLE_DATA_DIR`, or the repo's `sample-data/` directory if that variable is unset. The default path is two levels above `backend/app/config.py`. Findings stay in memory. Postgres is not required for this path.

### Frontend dashboard

Use Node 20. That is what CI and the frontend image use. `package-lock.json` is in the repo, so install from it:

```bash
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000. The page calls `NEXT_PUBLIC_API_BASE_URL`, which defaults to `http://localhost:8000`. Start the API first.

`npm run dev` reads that variable from the environment when the dev server starts. `npm run build` bakes it into the client bundle. Setting it only on an already-built container does not change the URL the browser calls.

`npm run lint` runs ESLint with `frontend/.eslintrc.json` (`next/core-web-vitals`). It does not start a setup prompt. CI does not run it. There is no frontend test script.

### Run the tests

From `backend/`, with the virtualenv activated:

```bash
python -m pytest
```

`backend/pytest.ini` already adds `-q` and points at `tests/`. There are 24 tests: scoring, adapters, controls, evidence, and the API. They use `sample-data/` and do not need Postgres or the frontend.

CI runs the same pytest command on Python 3.12 (`.github/workflows/backend-tests.yml`). The frontend workflow, on Node 20, typechecks and runs `npm run build`.

### Full stack with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

`.env` is optional. If it is missing, Compose uses the same defaults as `.env.example`.

| Service | Published port | What it does today |
| --- | --- | --- |
| `db` | 5432 | Postgres 16. The API does not connect to it. |
| `backend` | 8000 | FastAPI. Loads the mounted sample findings into memory. |
| `frontend` | 3000 | Next.js dashboard. The browser calls `http://localhost:8000`. |

`DATABASE_URL` is read in `backend/app/config.py` and never used. The store is in memory.

The backend image is still built from `backend/` only, so the sample files are not copied into it. `docker-compose.yml` mounts `./sample-data` on `/sample-data` (read-only) and sets `SAMPLE_DATA_DIR=/sample-data`. That is the directory the API reads at startup, so the findings list is the sample set. A plain `docker run` of the backend image, without that mount, still has an empty list.

The frontend image runs `npm run build` without `NEXT_PUBLIC_API_BASE_URL`, so the bundle keeps the default `http://localhost:8000`. That is the right host port for a browser on your machine. The Compose `environment` entry does not change a bundle that was already built.

---

## The endpoints I actually use

| Method | Path | What it gives me |
| --- | --- | --- |
| `GET` | `/health` | Liveness. No dependencies. |
| `GET` | `/` | Name, version, docs link, and how many findings were loaded |
| `GET` | `/findings` | Prioritized findings. Query filters: `source`, `severity`, `status`, `min_score` |
| `GET` | `/findings/{id}` | One finding, including its control mapping |
| `PATCH` | `/findings/{id}?status=` | Set `status` to `open`, `acknowledged`, `resolved`, or `suppressed`. Query parameter, not a JSON body. |
| `GET` | `/summary` | Counts by source, severity, status, and category |
| `GET` | `/controls` | Findings rolled up per control, per framework |
| `GET` | `/evidence` | Evidence pack as JSON. Markdown is the CLI (`python -m app.cli evidence`). |
| `POST` | `/ingest` | Re-read `sample-data/`, then score and map again |

Filter values: `source` is `aws`, `azure`, `endpoint`, or `github`. `severity` is `low`, `medium`, `high`, or `critical`. `min_score` is an integer from 0 to 100.

Full contract: [docs/api.md](docs/api.md).

---

## How it fits together

```
AWS / Azure / Endpoint / GitHub  (sample-data/<source>/findings.sample.json)
        │
        ▼  one adapter per source
  Ingestion adapters ──► normalized Finding (common model)
        │
        ▼
  Risk scoring engine  (severity + context → 0-100)
        │
        ▼
  Control mapper  (Finding.category → NIST CSF / CIS / PCI / SOX / FISMA)
        │
        ├──► FastAPI  ──►  Next.js dashboard
        └──► Evidence exporter  (JSON from the API; JSON + Markdown from the CLI)
```

More detail is in [docs/architecture.md](docs/architecture.md).

## Repository layout

`git clone` creates a `cloudriskiq/` directory:

```
cloudriskiq/
├── backend/
│   ├── app/
│   │   ├── adapters/     # aws, azure, github, endpoint → normalized Finding
│   │   ├── models.py     # the common Finding model + API shapes
│   │   ├── scoring.py    # transparent risk-scoring engine
│   │   ├── controls.py   # NIST CSF / CIS / PCI / SOX / FISMA mapping
│   │   ├── ingest.py     # sample-data → normalized + scored + mapped
│   │   ├── store.py      # in-memory store + dashboard/coverage rollups
│   │   ├── evidence.py   # audit evidence pack (JSON + Markdown)
│   │   ├── cli.py        # ingest / report / evidence from the terminal
│   │   ├── config.py     # env vars, including SAMPLE_DATA_DIR
│   │   └── main.py       # FastAPI app
│   ├── tests/
│   └── requirements.txt
├── frontend/             # Next.js dashboard
├── sample-data/          # synthetic findings per source
├── docs/
├── .github/workflows/    # backend pytest; frontend typecheck and build
└── docker-compose.yml
```

## Docs

- [Plan & strategy](docs/plan.md): goals, what it proves, roadmap
- [What I broke / fixed / built](docs/broke-fixed-built.md)
- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Data model](docs/data-model.md)
- [Security model](docs/security-model.md)
- [Résumé bullets](docs/resume-bullets.md)

## License

[MIT](LICENSE). Copyright (c) 2026 Matthew Coggins.
