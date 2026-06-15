# Résumé bullets

Bullets describing CloudRiskIQ. I keep these honest: only what's actually built.

## Current (everything below is implemented and tested)

- Built **CloudRiskIQ**, a full-stack security-findings platform (FastAPI ·
  Next.js/React · Python CLI) that normalizes findings across AWS, Azure,
  endpoint, and GitHub into one risk-scored, control-mapped view.
- Designed a transparent **risk-scoring engine** that adjusts raw severity by
  context (public exposure, asset criticality, exploit signal, compliance scope,
  age) to produce a defensible 0-100 prioritization, the same triage discipline
  I used to remediate 450+ SOX findings.
- Implemented **control mapping to NIST CSF 2.0, CIS Controls v8, PCI-DSS v4.0,
  SOX ITGC, and FISMA / NIST 800-53**, scope-aware so regulatory controls attach
  only to in-scope findings.
- Wrote a Python **evidence-collection exporter** that generates timestamped,
  deterministic audit packs (JSON + Markdown) mapping each finding to its
  controls, automating what I used to assemble by hand during SOX/PCI/FISMA
  audits.
- Built source-specific **ingestion adapters** that normalize heterogeneous
  findings into a common model behind one interface, so adding a source is one
  adapter and nothing downstream changes.
- Delivered a **Next.js dashboard** (risk KPIs, prioritized findings, control
  coverage) and a **24-test suite** (pytest) covering scoring, classification,
  control mapping, evidence generation, and the API; CI runs on GitHub Actions.

## Short version (one-liner)

- Built CloudRiskIQ: a FastAPI + Next.js platform that ingests AWS/Azure/GitHub/
  endpoint security findings, risk-scores them by context, maps each to NIST CSF/
  CIS/PCI/SOX/FISMA controls, and exports audit-ready evidence packs.

## Phrasing tips (note to self)

- Lead with the verb and the impact, not the tech list.
- Tie each bullet back to real audit experience; that's what makes it mine.
- Quantify where it's true (5 frameworks, 4 sources, 24 tests).
