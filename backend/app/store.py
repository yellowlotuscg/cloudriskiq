"""In-memory findings store + the aggregations the API and dashboard need.

I kept persistence out of the critical path on purpose: the store is an in-memory
list hydrated from the ingest pipeline at startup. That's enough to demo the whole
product offline, and it means `/health` (and the app) come up with zero external
dependencies. The data-model doc describes the Postgres schema this would back
onto in production; swapping this class for a repository over SQLAlchemy is a
contained change.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional

from app.controls import frameworks_in_use
from app.models import (
    ControlCoverage,
    Finding,
    FrameworkCoverage,
    Severity,
    SeverityCount,
    Source,
    Status,
    Summary,
)


class FindingsStore:
    def __init__(self) -> None:
        self._findings: Dict[str, Finding] = {}

    # ---- lifecycle ----
    def replace_all(self, findings: List[Finding]) -> None:
        self._findings = {f.id: f for f in findings}

    def count(self) -> int:
        return len(self._findings)

    # ---- reads ----
    def list(
        self,
        source: Optional[Source] = None,
        severity: Optional[Severity] = None,
        status: Optional[Status] = None,
        min_score: Optional[int] = None,
    ) -> List[Finding]:
        items = list(self._findings.values())
        if source is not None:
            items = [f for f in items if f.source == source]
        if severity is not None:
            items = [f for f in items if f.severity == severity]
        if status is not None:
            items = [f for f in items if f.status == status]
        if min_score is not None:
            items = [f for f in items if f.risk_score >= min_score]
        items.sort(key=lambda f: f.risk_score, reverse=True)
        return items

    def get(self, finding_id: str) -> Optional[Finding]:
        return self._findings.get(finding_id)

    def set_status(self, finding_id: str, status: Status) -> Optional[Finding]:
        finding = self._findings.get(finding_id)
        if finding is None:
            return None
        finding.status = status
        return finding

    # ---- aggregations ----
    def summary(self) -> Summary:
        items = list(self._findings.values())
        by_source = Counter(f.source.value for f in items)
        by_status = Counter(f.status.value for f in items)
        by_category = Counter(f.category.value for f in items)
        sev = Counter(f.severity.value for f in items)
        sev_count = SeverityCount(
            low=sev.get("low", 0),
            medium=sev.get("medium", 0),
            high=sev.get("high", 0),
            critical=sev.get("critical", 0),
        )
        open_crit_high = sum(
            1
            for f in items
            if f.status == Status.open and f.severity in (Severity.high, Severity.critical)
        )
        avg = round(sum(f.risk_score for f in items) / len(items), 1) if items else 0.0
        top = sorted(items, key=lambda f: f.risk_score, reverse=True)[:5]
        return Summary(
            total=len(items),
            by_source=dict(by_source),
            by_severity=sev_count,
            by_status=dict(by_status),
            by_category=dict(by_category),
            open_critical_high=open_crit_high,
            average_risk_score=avg,
            top_findings=top,
        )

    def control_coverage(self) -> ControlCoverage:
        """Roll findings up by control so an auditor can see, per control, which
        findings are open against it and the worst risk in that bucket."""
        buckets: Dict[tuple, Dict] = defaultdict(
            lambda: {"title": "", "finding_ids": [], "max_risk": 0}
        )
        for f in self._findings.values():
            for ref in f.controls:
                key = (ref.framework, ref.control_id)
                b = buckets[key]
                b["title"] = ref.title
                b["finding_ids"].append(f.id)
                b["max_risk"] = max(b["max_risk"], f.risk_score)

        controls = [
            FrameworkCoverage(
                framework=fw,
                control_id=cid,
                title=b["title"],
                finding_count=len(b["finding_ids"]),
                max_risk_score=b["max_risk"],
                finding_ids=sorted(b["finding_ids"]),
            )
            for (fw, cid), b in buckets.items()
        ]
        controls.sort(key=lambda c: (c.framework, -c.max_risk_score, c.control_id))
        return ControlCoverage(frameworks=frameworks_in_use(), controls=controls)


# Process-wide singleton, hydrated on startup (see app.main).
store = FindingsStore()
