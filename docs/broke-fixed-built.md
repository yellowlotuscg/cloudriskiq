# What I broke / fixed / built

This is the writeup I'd actually walk an interviewer through. It's not a war
story about taking prod down — CloudRiskIQ is a build project — so "broke" here
means the *problem I kept hitting* in real audit work, and the rest is what I did
about it.

## What was broken (the problem)

For 11+ years I was the primary technical contact for SOX, PCI-DSS, and FISMA
audits. Two things were broken every single time:

1. **Severity is not risk.** Every scanner — Security Hub, Defender for Cloud,
   Qualys, GitHub — hands you a wall of `HIGH` / `MEDIUM` / `LOW`. But a `HIGH`
   on a public, production bucket holding cardholder data is a completely
   different risk than a `HIGH` on an internal dev box, and the scanner scores
   them the same. So "what do I fix first?" — the only question that matters when
   you've got 450+ open findings — was a manual triage exercise every time.

2. **Evidence was hand-assembled.** When the auditor pointed at a finding and
   said "which control does this map to, and show me the evidence," that mapping
   lived in a spreadsheet that someone maintained by hand, and the evidence was
   screenshots pasted into a binder. It was slow, error-prone, and stale the
   moment the environment changed.

## What I fixed (the approach)

**Risk scoring that accounts for context.** `app/scoring.py` starts from the
severity base score and adjusts it by the things that actually change the risk:

- public exposure (`+10`)
- exploit signal — known CVE, leaked secret, open admin port (`+8`)
- asset criticality, derived from prod/non-prod + data classification (`-5…+8`)
- compliance scope — PCI/SOX/FISMA in play means real regulatory pressure
  (`+3` per regime, capped at `+6`)
- age — an open finding that's lingered for 90+ days is a worse risk than a fresh
  one (`+3…+9`)

The weighting is deliberately simple and additive. I'd rather defend a
transparent model to an auditor than ship a black box — when someone asks "why
is this a 98?", I can answer to the point.

**Control mapping that isn't manual.** `app/controls.py` is a readable lookup
table: every finding is classified into a `Category` by its adapter, and each
category maps to the controls it touches. NIST CSF and CIS apply to everything
(my hardening baseline); PCI / SOX / FISMA only attach when the finding is
actually in that compliance scope, so a PCI control never shows up against a box
that doesn't touch cardholder data. That gives me the traceability auditors want,
generated instead of typed.

**Evidence on demand.** `app/evidence.py` turns the live state into a
timestamped, deterministic evidence pack — machine-readable JSON plus a Markdown
report that drops straight into an audit binder. Same idea as the Python
evidence-collection tooling I built on the job, applied to the normalized data.

## What I built (the deliverable)

A working full-stack application, runnable on a laptop with synthetic data and no
cloud credentials:

- **Ingestion adapters** (`app/adapters/`) — one per source (AWS, Azure, GitHub,
  endpoint). Each takes that source's real-world shape and normalizes it to one
  common `Finding`. The rest of the system never sees source-specific JSON.
- **Risk scoring engine** — described above; 0–100, clamped, explainable.
- **Control mapper** — five frameworks, scope-aware.
- **FastAPI service** — `/findings`, `/summary`, `/controls`, `/evidence`, plus
  status updates and re-ingest. Auto-generated Swagger docs.
- **Next.js dashboard** — KPIs, a prioritized findings table colored by risk, and
  a control-coverage table.
- **CLI** — same engine from the terminal (`ingest`, `report`, `evidence`), so it
  fits a CI job or a scheduled evidence run.
- **Tests** — 24 of them across scoring, adapters, control mapping, evidence
  generation, and the API.

## What I'd do next

- Persist to the PostgreSQL schema in [data-model.md](data-model.md) and keep a
  `FindingEvent` history for a full audit trail of who changed what, when.
- Replace the sample-data file reads with live source clients (Security Hub,
  Defender for Cloud, GitHub API) behind the same adapter interface — nothing
  downstream changes.
- Add authn/authz (read-only viewer vs. responder) before this is anything but a
  local demo.
