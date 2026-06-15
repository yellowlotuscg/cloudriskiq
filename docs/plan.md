# Plan & strategy

## Why this project exists

I want a portfolio piece that proves the GRC/security work I've actually done for
11+ years, in a form someone can clone and run in five minutes. Certs (CISSP and
AZ-500, both in progress) say I studied; this says I can build. The goal is a repo
I can put next to my résumé and talk through in an interview without hand-waving —
because I wrote every line and can explain every decision.

## What it's meant to demonstrate

1. **I understand controls, not just findings.** Mapping technical findings to
   NIST CSF, CIS, PCI-DSS, SOX, and FISMA is the core of GRC work, and it's the
   center of this repo.
2. **I can prioritize.** A risk-scoring engine that turns 19 findings into a
   defensible "fix this first" order — the same skill behind remediating 450+ SOX
   findings without boiling the ocean.
3. **I can automate evidence.** The evidence exporter is the software version of
   the Python tooling I built to survive audit season.
4. **I can ship working software.** Normalized data model, adapters, an API, a
   UI, a CLI, and tests — kept runnable at every step.

## Design principles I held to

- **Normalize early.** Adapters convert source shapes to one model at ingest;
  everything downstream is source-agnostic. Adding a fifth source is one adapter.
- **Keep it explainable.** Scoring and control mapping are plain, readable code —
  no ML black box — because I have to defend the output to an auditor.
- **Runnable with zero credentials.** Sample data + in-memory store means `git
  clone` → running app. No AWS keys, no database, no excuses.
- **Test the logic that matters.** Scoring, classification, and control mapping
  are where bugs would quietly corrupt an audit, so those are covered.

## Roadmap

| Stage | Status |
| --- | --- |
| Scaffold: health endpoint, compose, CI, docs | ✅ done |
| Normalized model + per-source adapters | ✅ done |
| Risk-scoring engine | ✅ done |
| Control mapping (NIST CSF / CIS / PCI / SOX / FISMA) | ✅ done |
| Evidence pack export (JSON + Markdown) | ✅ done |
| Dashboard (KPIs, findings, control coverage) | ✅ done |
| CLI (ingest / report / evidence) | ✅ done |
| PostgreSQL persistence + `FindingEvent` history | ▢ next |
| Live source clients behind the adapter interface | ▢ next |
| AuthN/AuthZ (viewer vs. responder) | ▢ next |

## How I'd talk about it in an interview

"I was the person auditors came to. The two things that always hurt were
prioritizing a huge backlog of findings and producing control-mapped evidence by
hand. So I built the tool that does both: it scores findings by real risk, maps
each one to the frameworks it touches, and exports an evidence pack on demand. It
runs offline on synthetic data so you can see the whole thing work, and I can walk
you through any piece of it because I built it."
