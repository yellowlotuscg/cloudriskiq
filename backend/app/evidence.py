"""Evidence collection.

When I was the primary technical contact for SOX/PCI/FISMA audits, the single most
time-consuming thing was producing *evidence*: a defensible, timestamped artifact
that says "here is the control, here is what we observed, here is the disposition."
I automated a lot of that with Python. This module is the same idea applied to
CloudRiskIQ's normalized findings: it turns the current state into an evidence
pack — machine-readable JSON plus a human-readable Markdown report — that maps each
finding to its controls and records its status.

It's deliberately read-only and deterministic so the same inputs always produce the
same pack (minus the generation timestamp), which is exactly what an auditor wants.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from app.models import Finding
from app.store import FindingsStore


def build_evidence_pack(store: FindingsStore, generated_at: str = None) -> Dict:
    """Assemble a structured evidence pack from the current store state."""
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    summary = store.summary()
    coverage = store.control_coverage()
    findings = store.list()

    records: List[Dict] = []
    for f in findings:
        records.append(
            {
                "finding_id": f.id,
                "source": f.source.value,
                "title": f.title,
                "severity": f.severity.value,
                "category": f.category.value,
                "resource": f.resource,
                "risk_score": f.risk_score,
                "status": f.status.value,
                "first_seen": f.first_seen,
                "compliance_scope": f.compliance_scope,
                "controls": [
                    {"framework": c.framework, "control_id": c.control_id, "title": c.title}
                    for c in f.controls
                ],
            }
        )

    return {
        "report": "CloudRiskIQ Control Evidence Pack",
        "generated_at": generated_at,
        "frameworks": coverage.frameworks,
        "summary": {
            "total_findings": summary.total,
            "open_critical_high": summary.open_critical_high,
            "average_risk_score": summary.average_risk_score,
            "by_severity": summary.by_severity.model_dump(),
            "by_source": summary.by_source,
            "by_status": summary.by_status,
        },
        "control_coverage": [c.model_dump() for c in coverage.controls],
        "findings": records,
    }


def render_markdown(pack: Dict) -> str:
    """Render an evidence pack as a Markdown report suitable for an audit binder."""
    lines: List[str] = []
    lines.append(f"# {pack['report']}")
    lines.append("")
    lines.append(f"_Generated: {pack['generated_at']}_")
    lines.append("")
    lines.append("> Synthetic demonstration data — not a real control assessment.")
    lines.append("")

    s = pack["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total findings: **{s['total_findings']}**")
    lines.append(f"- Open critical/high: **{s['open_critical_high']}**")
    lines.append(f"- Average risk score: **{s['average_risk_score']}**")
    sev = s["by_severity"]
    lines.append(
        f"- By severity: critical {sev['critical']} · high {sev['high']} · "
        f"medium {sev['medium']} · low {sev['low']}"
    )
    lines.append(f"- Frameworks in scope: {', '.join(pack['frameworks'])}")
    lines.append("")

    lines.append("## Control coverage")
    lines.append("")
    lines.append("| Framework | Control | Title | Findings | Max risk |")
    lines.append("| --- | --- | --- | ---: | ---: |")
    for c in pack["control_coverage"]:
        lines.append(
            f"| {c['framework']} | {c['control_id']} | {c['title']} | "
            f"{c['finding_count']} | {c['max_risk_score']} |"
        )
    lines.append("")

    lines.append("## Findings (highest risk first)")
    lines.append("")
    lines.append("| Risk | Severity | Source | Finding | Resource | Status | Controls |")
    lines.append("| ---: | --- | --- | --- | --- | --- | --- |")
    for r in pack["findings"]:
        ctrls = ", ".join(f"{c['framework']} {c['control_id']}" for c in r["controls"]) or "—"
        lines.append(
            f"| {r['risk_score']} | {r['severity']} | {r['source']} | {r['title']} | "
            f"`{r['resource']}` | {r['status']} | {ctrls} |"
        )
    lines.append("")
    return "\n".join(lines)
