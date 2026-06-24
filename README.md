# CloudRiskIQ

A case study from [Yellow Lotus Consulting Group](https://yellowlotuscg.com) demonstrating security and compliance engineering, built on synthetic data (not client data).

I spent 11+ years on the GRC side of the house. I was the primary technical contact for
SOX, PCI-DSS, and FISMA audits, the person who had to turn a pile of scanner
output into "here's the control, here's the evidence, here's what we're fixing
first." CloudRiskIQ is me building the tool I always wanted during those audits.

It ingests security findings from **AWS, Azure, endpoints, and GitHub**,
normalizes them into one model, scores each one by *risk* (not just raw
severity), and maps every finding to the controls it touches across **NIST CSF
2.0, CIS Controls v8, PCI-DSS v4.0, SOX ITGC, and FISMA / NIST 800-53**. Then it
generates an audit-ready evidence pack from the live state.

It runs end-to-end on a laptop with **synthetic data and no cloud credentials**.

> **Heads up:** all sample findings are synthetic. No real accounts, resources,
> or secrets are in this repo.

---

## What I broke / fixed / built

Recruiters keep saying the same thing: skip the cert wall, show me that you
broke something, fixed something, and built something, and show me how you
think. So, plainly:

- **Broke:** In real audits I watched teams drown in raw scanner output. A
  console full of "HIGH" findings tells you nothing about *what to fix first*.
  A HIGH on a public, production, cardholder-data bucket is not the same risk as
  a HIGH on an internal dev box, but the scanner scores them identically. And
  when the auditor asked "which control does this map to, and show me the
  evidence," that traceability lived in someone's spreadsheet, by hand.
- **Fixed:** I built a transparent risk-scoring engine that adjusts severity by
  context (public exposure, asset criticality, exploit signal, compliance scope,
  age) so the list sorts by *what actually matters*. And I built a control mapper
  that turns every technical finding into framework references automatically, so
  the "map it to a control + produce evidence" step isn't manual anymore.
- **Built:** A working full-stack app. FastAPI backend (ingestion adapters,
  scoring, control mapping, evidence export), a Next.js dashboard, a CLI, and a
  test suite. See the full writeup in
  [docs/broke-fixed-built.md](docs/broke-fixed-built.md).

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

### Backend + CLI (no Docker, no database)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload --port 8000
#   http://localhost:8000/docs   (Swagger UI)

# …or drive the same engine from the CLI
python -m app.cli ingest                 # load + score, print a summary
python -m app.cli report                 # prioritized findings table
python -m app.cli evidence --out ./out    # write JSON + Markdown evidence pack
```

The app hydrates from `sample-data/` at startup, so every endpoint returns real
(synthetic) findings immediately.

### Frontend dashboard

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000  (expects the API on :8000)
```

### Run the tests

```bash
cd backend && source .venv/bin/activate
python -m pytest -q          # 24 tests: scoring, adapters, controls, evidence, API
```

### Full stack with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

---

## The endpoints I actually use

| Method | Path | What it gives me |
| --- | --- | --- |
| `GET` | `/health` | Liveness, no dependencies, always answers |
| `GET` | `/findings` | Prioritized findings; filter by `source`, `severity`, `status`, `min_score` |
| `GET` | `/findings/{id}` | One finding with its full control mapping |
| `PATCH` | `/findings/{id}` | Acknowledge / resolve / suppress |
| `GET` | `/summary` | Dashboard rollups (by source / severity / status / category) |
| `GET` | `/controls` | Coverage: every finding rolled up per control, per framework |
| `GET` | `/evidence` | A structured control evidence pack |
| `POST` | `/ingest` | Re-run ingestion from `sample-data/` |

Full contract: [docs/api.md](docs/api.md).

---

## How it fits together

```
AWS / Azure / Endpoint / GitHub  (sample-data/*.json)
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
        └──► Evidence exporter  (JSON + Markdown audit pack)
```

More detail and the design decisions are in
[docs/architecture.md](docs/architecture.md).

## Repository layout

```
cloudriskiq/
├── backend/app/
│   ├── adapters/     # aws, azure, github, endpoint → normalized Finding
│   ├── models.py     # the common Finding model + API shapes
│   ├── scoring.py    # transparent risk-scoring engine
│   ├── controls.py   # NIST CSF / CIS / PCI / SOX / FISMA mapping
│   ├── ingest.py     # sample-data → normalized + scored + mapped
│   ├── store.py      # in-memory store + dashboard/coverage rollups
│   ├── evidence.py   # audit evidence pack (JSON + Markdown)
│   ├── cli.py        # ingest / report / evidence from the terminal
│   └── main.py       # FastAPI app
├── frontend/         # Next.js dashboard
├── sample-data/      # synthetic findings per source
├── docs/             # architecture, plan & strategy, broke-fixed-built, ...
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
